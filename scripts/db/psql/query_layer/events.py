from sqlalchemy.orm import Session

from scripts.logging.logging import logger
from scripts.utils.postgres_util import PostgresUtility


class EventsPSQL:
    def __init__(self, db: Session, table_obj, project_id=None):
        self.project_id = project_id
        self.session: Session = db
        self.table_obj = table_obj
        self.postgres_utility_obj = PostgresUtility(session=db, table=self.table_obj)
        # self.postgres_utility_obj.create_table()

    def find_data_by_raw_query(self, raw_query):
        try:
            data = self.postgres_utility_obj.fetch_records_by_raw_query(
                raw_query=raw_query
            )
            return data
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            return None
