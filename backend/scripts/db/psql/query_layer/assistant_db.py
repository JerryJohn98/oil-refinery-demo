from sqlalchemy.orm import Session

from scripts.core.constants.query_constants import AssistantDBQueryConstants
from scripts.db.psql.query_layer.common_query import CommonPSQL
from scripts.logging.logging import logger
from scripts.utils.common_utils import CommonUtils


class AssistantDBPSQL:
    def __init__(self, db: Session, project_id=None):
        self.project_id = project_id
        self.common_utils = CommonUtils(project_id=self.project_id)
        self.common_pg_obj = CommonPSQL(db=db, project_id=self.project_id)

    def find_production_plan_by_condition(
        self, hierarchy_data, query=None, order_by_query=""
    ):
        try:
            hierarchy_query, _ = self.common_utils.generate_combined_hierarchy_query(
                hierarchy_data
            )
            if not hierarchy_query:
                return []
            hierarchy_query = (
                f"{hierarchy_query} AND {query}" if query else hierarchy_query
            )
            final_query = (
                AssistantDBQueryConstants.production_plan_query_for_prv.format(
                    filter_query=hierarchy_query
                )
                + order_by_query
            )
            data = self.common_pg_obj.find_all_data_by_raw_query(raw_query=final_query)
            return data
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            return None

    def fetch_activity_event_data(
        self,
        hierarchy_data,
        current_timestamp,
        request_data,
        actual_date_range_filter,
        scheduled_date_range_filter,
    ):
        """Custom function to identify the current & next event from all the category- \
        Asset Care, Shutdown, Production, Unscheduled"""

        filter_query = actual_date_range_filter.format(
            start_time_value=current_timestamp,
            end_time_value=current_timestamp,
            tz=request_data.tz,
        )

        filter_query_unscheduled = scheduled_date_range_filter.format(
            end_time_value=current_timestamp, tz=request_data.tz
        )
        # Generate the base hierarchy query
        hierarchy_tag, _ = self.common_utils.generate_combined_hierarchy_query(
            hierarchy_data
        )

        if filter_query:
            hierarchy_query = f"{hierarchy_tag} AND {filter_query} {AssistantDBQueryConstants.order_by_constraint}"
            production_hierarchy = (
                f"{hierarchy_tag} AND"
                f" {filter_query}"
                f" {AssistantDBQueryConstants.production_plan_progress}"
                f" {AssistantDBQueryConstants.order_by_constraint}"
            )

        # Define queries dynamically
        queries = {
            "asset_care": AssistantDBQueryConstants.asset_care_plan_view_query.format(
                filter_query=hierarchy_query, tz=request_data.tz
            ),
            "shut_down": AssistantDBQueryConstants.shut_down_query.format(
                filter_query=hierarchy_query, tz=request_data.tz
            ),
            "production_table": AssistantDBQueryConstants.production_plan_query.format(
                filter_query=production_hierarchy, tz=request_data.tz
            ),
        }

        if filter_query_unscheduled:
            order_by_constraint = AssistantDBQueryConstants.order_by_constraint.replace(
                "start_time", "scheduled_start_time"
            )
            updated_hierarchy_query = (
                f"{hierarchy_tag} AND {filter_query_unscheduled} {order_by_constraint}"
            )
        else:
            updated_hierarchy_query = hierarchy_query

        queries["unscheduled"] = AssistantDBQueryConstants.production_plan_query.format(
            filter_query=updated_hierarchy_query, tz=request_data.tz
        )

        return {
            table: self.common_pg_obj.find_all_data_by_raw_query(raw_query=query)
            for table, query in queries.items()
        }
