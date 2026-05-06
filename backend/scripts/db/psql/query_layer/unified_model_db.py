from sqlalchemy.orm import Session

from scripts.core.constants.query_constants import UnifiedModelDBQueryConstants
from scripts.db.psql.query_layer.common_query import CommonPSQL
from scripts.logging.logging import logger
from scripts.utils.common_utils import CommonUtils


class UnifiedModelDBPSQL:
    def __init__(self, db: Session, project_id=None):
        self.project_id = project_id
        self.common_utils = CommonUtils(project_id=self.project_id)
        self.common_pg_obj = CommonPSQL(db=db, project_id=self.project_id)

    def find_hierarchy(self, hierarchy_data, columns="*", query=None):
        try:
            columns = (
                ", ".join(str(each) for each in columns)
                if isinstance(columns, list)
                else columns
            )
            hierarchy_query, _ = self.common_utils.generate_combined_hierarchy_query(
                hierarchy_data
            )
            if not hierarchy_query:
                return []
            hierarchy_query = (
                f"{hierarchy_query} AND {query}" if query else hierarchy_query
            )
            final_query = UnifiedModelDBQueryConstants.hierarchy_query.format(
                columns=columns, filter_query=hierarchy_query
            )
            data = self.common_pg_obj.find_all_data_by_raw_query(raw_query=final_query)
            return data
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            return None

    def get_equipments_based_on_line(self, hierarchy_data):
        """

        :param line_id:
        :return:
        """
        equipment_data = []
        try:
            equipment_hierarchy_filter_query, _ = (
                self.common_utils.generate_equal_hierarchy_query(
                    hierarchy_data, column="parent_hierarchy"
                )
            )
            final_query = UnifiedModelDBQueryConstants.equipment_query.format(
                filter_query=equipment_hierarchy_filter_query
            )
            equipment_data = self.common_pg_obj.find_all_data_by_raw_query(
                raw_query=final_query
            )
            equipment_hierarchy_map = {
                item["hierarchy"]: item["equipment_name"] for item in equipment_data
            }
            hierarchy_list = [item["hierarchy"] for item in equipment_data]
            return equipment_data, equipment_hierarchy_map, hierarchy_list
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            return equipment_data


    def get_lines_based_on_area(self, hierarchy_data):
        """

        :param line_id:
        :return:
        """
        line_data = []
        try:
            equipment_hierarchy_filter_query, _ = (
                self.common_utils.generate_equal_hierarchy_query(
                    hierarchy_data, column="parent_hierarchy"
                )
            )
            final_query = UnifiedModelDBQueryConstants.line_query.format(
                filter_query=equipment_hierarchy_filter_query
            )
            line_data = self.common_pg_obj.find_all_data_by_raw_query(
                raw_query=final_query
            )
            line_hierarchy_map = {
                item["hierarchy"]: item["line_name"] for item in line_data
            }
            hierarchy_list = [item["hierarchy"] for item in line_data]
            return line_data, line_hierarchy_map, hierarchy_list
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            return line_data

    def get_line_info_based_on_line(self, hierarchy_data):
        """

        :param line_id:
        :return:
        """
        line_data = []
        try:
            equipment_hierarchy_filter_query, _ = (
                self.common_utils.generate_equal_hierarchy_query(
                    hierarchy_data, column="level_id"
                )
            )
            final_query = UnifiedModelDBQueryConstants.line_query.format(
                filter_query=equipment_hierarchy_filter_query
            )
            line_data = self.common_pg_obj.find_all_data_by_raw_query(
                raw_query=final_query
            )
            line_hierarchy_map = {
                item["hierarchy"]: item["line_name"] for item in line_data
            }
            hierarchy_list = [item["hierarchy"] for item in line_data]
            return line_data, line_hierarchy_map, hierarchy_list
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            return line_data

