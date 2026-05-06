from dbm import error
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing_extensions import final

from scripts.core.constants.query_constants import UnifiedModelDBQueryConstants, EventsDBQueryConstants
from scripts.logging.logging import logger
from scripts.utils.postgres_util import PostgresUtility


class CommonPSQL:
    def __init__(self, db: Session, table_obj=None, project_id=None):
        self.project_id = project_id
        self.session: Session = db
        self.table_obj = table_obj
        self.postgres_utility_obj = PostgresUtility(session=db, table=self.table_obj)
        # self.postgres_utility_obj.create_table()

    def find_one_data_by_raw_query(self, raw_query):
        try:
            data = self.postgres_utility_obj.fetch_record_by_raw_query(
                raw_query=raw_query
            )
            return data
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            return None

    def find_all_data_by_raw_query(self, raw_query):
        try:
            data = self.postgres_utility_obj.fetch_records_by_raw_query(
                raw_query=raw_query
            )
            return data
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            return None

    def fetch_po_changeover_data(self, start_time, end_time, tz, query, filter_query):
        try:
            raw_query = text(query.format(tz=tz, filter_query=filter_query))
            result = self.session.execute(
                raw_query, {"start_time": start_time, "end_time": end_time}
            ).fetchall()

            return result or None

        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            raise fetch_error

    def fetch_equipment_labels(self, equipment_id_list, line_id, columns="name"):
        try:
            # Prepare equipment query
            filter_query = f"WHERE id IN ({', '.join(map(repr, equipment_id_list))}) AND line = '{line_id}'"
            equipment_query = UnifiedModelDBQueryConstants.equipment_query.format(
                columns=columns, filter_query=filter_query
            )

            # Fetch equipment data
            equipment_data = self.find_all_data_by_raw_query(equipment_query)
            return equipment_data
        except Exception as ex:
            logger.error(f"Failed to fetch equipment: {ex}")
            raise ex

    def fetch_top_equipment_hierarchy(
            self, hierarchy_list, sort, limit, start_time, end_time, tz,
            start_time_with_tz, end_time_with_tz, ):
        try:
            sort_key = sort
            machine_limit = (
                f" LIMIT {limit}" if limit else ""
            )
            hierarchy_list_str = ",".join([f"'{key}'" for key in hierarchy_list])
            filter_query = f" where hierarchy in ({hierarchy_list_str})"
            filter_query += f" AND {start_time_with_tz} <= '{end_time}' AND {end_time_with_tz} >= '{start_time}'"

            final_query = EventsDBQueryConstants.stops_view_query.format(
                filter_query=filter_query,
                tz=tz,
                input_start_date=start_time,
                input_end_date=end_time,
                sort_key=sort_key,
                limit_query=machine_limit,
            )
            final_data = self.find_all_data_by_raw_query(raw_query=final_query)
            return final_data
        except Exception as Error:
                logger.error(f"Failed to fetch equipment: {error}")
                raise error
