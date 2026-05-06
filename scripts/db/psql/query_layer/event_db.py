from sqlalchemy import text
from sqlalchemy.orm import Session

from scripts.core.constants.query_constants import (
    EventsDBQueryConstants,
    QueryConstants,
)
from scripts.db.psql.query_layer.common_query import CommonPSQL
from scripts.logging.logging import logger
from scripts.utils.common_utils import CommonUtils


class EventDBPSQL:
    def __init__(self, db: Session, project_id=None):
        self.project_id = project_id
        self.session: Session = db
        self.common_utils = CommonUtils(project_id=self.project_id)
        self.common_pg_obj = CommonPSQL(db=db, project_id=self.project_id)

    def find_events_view_by_condition(
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
                EventsDBQueryConstants.events_view_query_for_prv.format(
                    filter_query=hierarchy_query
                )
                + order_by_query
            )
            data = self.common_pg_obj.find_all_data_by_raw_query(raw_query=final_query)
            return data
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            return None

    def fetch_downtime_data(self, start_time, end_time, tz, hierarchy_query):
        try:
            raw_query = text(
                QueryConstants.downtime_query.format(
                    tz=tz, hierarchy_query=hierarchy_query
                )
            )
            result = self.session.execute(
                raw_query, {"start_time": start_time, "end_time": end_time}
            ).fetchone()

            total_duration_hours = result[3] if result and result[3] is not None else ""
            return total_duration_hours

        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            raise fetch_error

    def find_one_data_by_raw_query(self, raw_query):
        try:
            data = self.common_pg_obj.find_one_data_by_raw_query(raw_query=raw_query)
            return data
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            return None

    def find_all_data_by_raw_query(self, raw_query):
        try:
            data = self.common_pg_obj.find_all_data_by_raw_query(raw_query=raw_query)
            return data
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            return None

    def find_events_by_condition(
        self, hierarchy_data, query=None, order_by_query="", tz=""
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
                EventsDBQueryConstants.events_view_query.format(
                    filter_query=hierarchy_query, tz=tz
                )
                + order_by_query
            )
            data = self.common_pg_obj.find_all_data_by_raw_query(raw_query=final_query)
            return data
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            return None
