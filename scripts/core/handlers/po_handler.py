from datetime import datetime
from typing import Dict, List, Optional, Union
from sqlalchemy.orm import Session
from scripts.core.constants.po_queries import POQueries
from scripts.core.utils.postgres_util import PostgresUtility
from scripts.logging.logging import logger
from scripts.utils.common_utils import CommonUtils



class POHandler:
    VALID_CALCULATION_CYCLES = {"post_changeover", "post_maintenance"}

    def __init__(
            self, project_id, assistant_db=None, unified_model_db=None, event_db=None, oee_db=None,
            shift_planning_db=None
    ):
        self.project_id = project_id
        self.project_id = project_id
        self.shift_planning_db_obj = None
        if assistant_db:
            self.assistant_pg_util = PostgresUtility(session=assistant_db)
        if event_db:
            self.event_pg_util = PostgresUtility(session=event_db)
        if unified_model_db:
            self.unified_model_pg_util = PostgresUtility(session=unified_model_db)
        if oee_db:
            self.oee_pg_util = PostgresUtility(session=oee_db)
        if shift_planning_db:
            self.shift_planning_db_obj = PostgresUtility(session=shift_planning_db)
        self.common_utils = CommonUtils(project_id=self.project_id, shift_planning_db_obj=self.shift_planning_db_obj)

    def get_query(self, calculation_cycle: str) -> Optional[str]:
        query_map = {
            "post_changeover": POQueries.POST_CHANGEOVER_QUERY,
            "post_maintenance": POQueries.POST_MAINTENANCE_QUERY,
        }
        return query_map.get(calculation_cycle)

    def format_query_with_params(self, query: str, params: dict) -> str:
        """Format the raw query with parameters directly into the query string."""
        formatted_query = query
        for key, value in params.items():
            if value is None:
                formatted_value = "NULL"
            elif isinstance(value, str):
                formatted_value = f"'{value}'"
            else:
                formatted_value = str(value)
            formatted_query = formatted_query.replace(f":{key}", formatted_value)
        return formatted_query

    def get_process_order(self, request_data):
        try:
            if request_data.calculation_cycle == "":
                return {"po": [], "default": None}
            calculation_cycle = request_data.calculation_cycle.strip() if request_data.calculation_cycle else "post_changeover"
            if calculation_cycle not in self.VALID_CALCULATION_CYCLES:
                return {"error": f"Invalid calculation_cycle value. Must be one of {self.VALID_CALCULATION_CYCLES}"}
            time_blocks,cte_query = self.common_utils.extract_stime_etime(request_data)
            query = self.get_query(calculation_cycle)
            if not query:
                return {"error": "No query found for the specified calculation cycle"}
            # print(query.format(cte_timeblock_query=cte_query))
            try:
                hierarchy_data = request_data.selected_hierarchy.filterData.get(
                    "hierarchy", {}
                )
            except Exception:
                hierarchy_data = request_data.widget_filter.hierarchy

            if not hierarchy_data:
                return []

            filter_query, _ = self.common_utils.generate_combined_hierarchy_query(
                hierarchy_data=hierarchy_data
            )
            filter_query += " and oee is not null"
            po_data = self.oee_pg_util.fetch_records_by_raw_query(
                raw_query=query.format(cte_timeblock_query=cte_query,filter_query=filter_query)
            )

            if not po_data:
                return []

            return {
                "po": [
                    {
                        "label": record["po_value"],
                        "value": record["po_value"]
                    }
                    for record in po_data
                ],
                "default": po_data[0]["po_value"] if po_data else None  # Set the first po_value as default
            }


        except Exception as error:
            logger.error(f"PO fetch error: {error}", exc_info=True)
            raise ValueError("Failed to fetch PO data") from error

    def fetch_calculation_cycle_dropdown_data(self, request_data):
        try:
            dropdown_json = self.common_utils.load_json_from_file(
                "assets/calculation_cycle_dropdown.json"
            )
            dropdown_values = dropdown_json.get("dropdown_values", [])

            default_value = request_data.default if getattr(request_data, 'default', "").strip() else "post_changeover"

            return {
                "dropdown_values": dropdown_values,
                "default": default_value
            }
        except Exception as fetch_error:
            logger.error(f"Failed to fetch calculation cycle dropdown data: {fetch_error}", exc_info=True)
            raise
