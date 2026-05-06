from scripts.core.constants.query_constants import ProductionPlanQuery
from scripts.core.constants.time_formats import AppTimeFormats
from scripts.core.engine.time_calculator import time_calc_std, parse_custom_filter_timestamp
from scripts.core.schemas.common_model import TimeCalcRequest
from scripts.db.mongo.ilens_configuration.collections.dynamic_hierarchy_details import (
    HierarchyDetailsCollection,
)
from scripts.db.psql.models.production import DBModelProduction
from scripts.db.psql.query_layer.production import ProductionPSQL
from scripts.logging.logging import logger
from scripts.utils.common_utils import CommonUtils
from scripts.utils.mongo_util import mongo_client


class DashboardHandler:
    def __init__(self, project_id, assistant_db=None):
        self.project_id = project_id
        self.common_utils = CommonUtils(project_id=self.project_id)
        self.assistant_db = assistant_db
        self.hierarchy_details_instance = HierarchyDetailsCollection(
            mongo_client=mongo_client, project_id=project_id
        )
        if self.assistant_db:
            self.production_pg_obj = ProductionPSQL(
                db=assistant_db, table_obj=DBModelProduction, project_id=self.project_id
            )

    def get_process_order(self, request_data):
        try:
            time_picker = request_data.selected_hierarchy.filterData.get(
                "timePickerValue", {}
            )

            custom_shift_time_picker = self.common_utils.update_custom_date_from_epoch(request_data.selected_hierarchy.filterData.get(
                "custom_shift_filter_date", {}
            ))


            request = {
                "widget_filter": {
                    "timePickerValue": time_picker
                },
                "tz": request_data.tz,
            }

            _, hierarchy_level_id = (
                self.common_utils.extract_accessible_hierarchy_node_id(
                    user_id=request_data.user_id
                )
            )
            hierarchy_data = request_data.selected_hierarchy.filterData.get(
                "hierarchy", {}
            )
            line_id = hierarchy_data.get(hierarchy_level_id.get("line", ""), "")
            if custom_shift_time_picker:
                start_time, end_time,_ = parse_custom_filter_timestamp(
                    req_body=custom_shift_time_picker, time_zone=request_data.tz
                )
            elif time_picker:
                start_time, end_time = time_calc_std(TimeCalcRequest(**request))
            else:
                return {}
            process_data = self.production_pg_obj.fetch_process_order(
                start_time=start_time,
                end_time=end_time,
                line_id=line_id,
                tz=request_data.tz,
            )

            # ongoing_po = ""
            ongoing_po = self.fetch_ongoing_production_plan(request_data.tz, hierarchy_data, start_time, end_time)
            ongoing_po = ongoing_po[0]["process_order"] if ongoing_po else ""
            return dict(po=process_data, default=ongoing_po)
        except Exception as error:
            logger.error(f"Failed to fetch the process order: {error}")
            raise error

    def fetch_ongoing_production_plan(self, tz, hierarchy_data, start_time, end_time):
        try:
            start_time_with_tz, end_time_with_tz = (
                self.common_utils.format_date_columns(
                    columns=[col],
                    tz=tz,
                    time_format=AppTimeFormats.USER_META_24_HR_FORMAT_YYYY_MM_DD,
                    use_alias=False,
                )
                for col in ["start_time", "end_time"]
            )

            filter_query, _ = self.common_utils.generate_equal_hierarchy_query(hierarchy_data, column="hierarchy")
            # ongoing_query = f"(CURRENT_TIMESTAMP AT TIME ZONE '{tz}' > start_time AT TIME ZONE '{tz}') AND (progress < 100)"
            query = f"{start_time_with_tz} <= '{end_time}' AND {end_time_with_tz} >= '{start_time}' AND (progress > 0 AND progress < 100)"
            filter_query += f"AND {query}"
            final_query = ProductionPlanQuery.production_plan_query.format(
                filter_query=filter_query,
            )

            final_data = self.production_pg_obj.find_all_data_by_raw_query(
                raw_query=final_query
            )
            return final_data
        except Exception as error:
            logger.error(f"Failed to fetch ongoing production plan: {error}")
            raise error