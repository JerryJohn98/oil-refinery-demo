from scripts.core.constants.query_constants import ProductionPlanQuery
from scripts.logging.logging import logger
from scripts.utils.postgres_util import PostgresUtility
from sqlalchemy import text
from sqlalchemy.orm import Session


class ProductionPSQL:
    def __init__(self, db: Session, table_obj, project_id=None):
        self.project_id = project_id
        self.session: Session = db
        self.table_obj = table_obj
        self.postgres_utility_obj = PostgresUtility(session=db, table=self.table_obj)
        # self.postgres_utility_obj.create_table()

    def fetch_process_order(self, start_time, end_time, line_id, tz):
        try:
            raw_query = text(ProductionPlanQuery.process_order_query.format(tz=tz))
            result = self.session.execute(
                raw_query,
                {"start_time": start_time, "end_time": end_time, "line_id": line_id},
            ).fetchall()

            if not result:
                return []

            final_result = [
                {"label": row["process_order"], "value": row["process_order"]}
                for row in result
            ]
            return final_result

        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            raise fetch_error

    def find_all_data_by_raw_query(self, raw_query):
        try:
            data = self.postgres_utility_obj.fetch_records_by_raw_query(
                raw_query=raw_query
            )
            return data
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            return None