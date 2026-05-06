from scripts.logging.logging import logger
from sqlalchemy import and_, func, inspect, text
from sqlalchemy.exc import SQLAlchemyError


class PostgresUtility:

    def __init__(self, session, table):
        self.session = session
        self.table = table

    def create_table(self):
        try:
            if self.session:
                engine = self.session.get_bind().engine
                if not inspect(engine).has_table(self.table.__tablename__):
                    self.table.__table__.create(bind=engine, checkfirst=True)
                else:
                    self.update_table_columns(engine)
                    orm_table = self.table
                    orm_table.__table__.create(bind=engine, checkfirst=True)
        except Exception as e:
            logger.error(f"Error occurred during start-up: {e}", exc_info=True)

    def update_table_columns(self, engine):
        inspector = inspect(engine)
        existing_columns = [
            column["name"] for column in inspector.get_columns(self.table.__tablename__)
        ]

        for column in self.table.__table__.columns:
            if column.name not in existing_columns:
                self.add_column(engine, self.table.__tablename__, column)

    @staticmethod
    def add_column(engine, table_name, column):
        column_definition = f"{column.name} {column.type}"
        engine.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")

    def find_all_data(self):
        try:
            query = self.session.query(self.table)
            data = query.all()
            data = self.fetch_records_from_object(data)
            return data
        except Exception as fetch_error:
            logger.error(f"Failed to fetch record: {fetch_error}")
            return None

    def find_many_data_including_foreign_values(
        self, filters: dict = None, column_mappings={}
    ):
        try:
            query = self.session.query(self.table)

            if filters:
                query = query.filter(
                    *[
                        getattr(self.table, key) == value
                        for key, value in filters.items()
                    ]
                )
            data = query.all()

            # Process the data into the desired format
            if column_mappings:
                result = [
                    {
                        **dict(row),
                        **{
                            label: row.get(value, None)
                            for label, value in column_mappings.items()
                            if value in row
                        },
                    }
                    for row in data
                ]
            else:
                result = [{**dict(row)} for row in data]
            return result
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            raise fetch_error

    def find_data_by_pagination(
        self, query, count_query, column_mappings={}, page: int = 1, page_size: int = 50
    ):
        try:
            # Calculate the offset for pagination
            offset = (page - 1) * page_size

            # SQL query for the data with joins and pagination
            data_query = text(query)

            # SQL query for the total count
            count_query = text(count_query)

            # Execute the count query to get the total records
            total_records = self.session.execute(count_query).scalar()

            # Execute the data query to fetch paginated records
            data = self.session.execute(
                data_query, {"page_size": page_size, "offset": offset}
            ).fetchall()

            # Process the data into the desired format
            if column_mappings:
                result = [
                    {
                        **dict(row),
                        **{
                            label: row[value]
                            for label, value in column_mappings.items()
                        },
                    }
                    for row in data
                ]
            else:
                result = [{**dict(row)} for row in data]

            # Calculate if there are more records to fetch
            end_of_records = offset + page_size >= total_records
            return result, end_of_records, total_records
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            raise fetch_error

    def find_data_by_condition(self, filters: dict = None, columns: list = None):
        """
        Fetch a single record using a raw query with dynamic filters.
        """
        try:
            if columns:
                query = self.session.query(
                    *[getattr(self.table, col) for col in columns]
                )
            else:
                query = self.session.query(self.table)

            if filters:
                query = query.filter(
                    *[
                        getattr(self.table, key) == value
                        for key, value in filters.items()
                    ]
                )

            record = query.one_or_none()
            if not record:
                return None

            # Return as dictionary if specific columns are selected
            if columns:
                return dict(zip(columns, record))

            # Convert full object to dictionary using utility method
            return self.fetch_record_from_object(record)
        except Exception as fetch_error:
            logger.error(f"Failed to fetch record: {fetch_error}")
            return None

    def find_many_data_by_condition(
        self, filters: dict = None, columns: list = None, distinct_column: str = None
    ):
        try:
            query = self.session.query(self.table)

            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(self.table, key) == value)

            # Apply distinct on the specified column if provided
            if distinct_column:
                query = query.distinct(getattr(self.table, distinct_column))

            # Select specific columns if provided
            if columns:
                query = query.with_entities(
                    *[getattr(self.table, col) for col in columns]
                )

            # Execute the query and fetch results
            records = query.all()
            if not records:
                return []

            # Return either a list of dictionaries or full objects based on columns
            return (
                [dict(zip(columns, record)) for record in records]
                if columns
                else [self.fetch_record_from_object(record) for record in records]
            )

        except Exception as fetch_error:
            logger.error(f"Failed to fetch records: {fetch_error}")
            return []

    def insert_or_update_record(self, data_to_insert: dict, filter_field: str):
        try:
            # Dynamically filter the entry based on the provided filter field and its value
            filter_value = data_to_insert.get(filter_field, 0)
            existing_entry = (
                self.session.query(self.table)
                .filter(getattr(self.table, filter_field) == filter_value)
                .first()
            )

            # Update the existing entry if found
            if existing_entry:
                for key, value in data_to_insert.items():
                    setattr(existing_entry, key, value)
                self.session.commit()
                logger.info("Data updated successfully!")
            else:
                # Insert a new entry if no existing record is found
                new_entry = self.table(**data_to_insert)
                self.session.add(new_entry)
                self.session.commit()
                logger.info(f"Data inserted successfully! {new_entry.__table__.name}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to insert or update data: {e}")
            raise

    def find_count(self, filters=None):
        try:
            query = self.session.query(self.table)

            if filters:
                query = query.filter_by(**filters)

            # Count the total number of rows
            total_count = query.with_entities(func.count()).scalar()
            logger.info(f"Total count fetched: {total_count}")
            return total_count
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch count: {e}")
            raise

    def delete_record(self, filters: dict, soft_delete: bool = True) -> bool:
        if not filters:
            logger.warning("No filters provided for deletion.")
            return False

        try:
            # Build the query with dynamic filters
            query = self.session.query(self.table)
            if len(filters) == 1:
                # Use filter_by if there is only one condition (more optimized)
                query = query.filter_by(**filters)
            else:
                # Use and_ for multiple conditions
                filter_conditions = [
                    getattr(self.table, key) == value for key, value in filters.items()
                ]
                query = query.filter(and_(*filter_conditions))

            # Fetch the entry to delete
            existing_entry = query.one_or_none()
            if not existing_entry:
                logger.warning(f"No record found with conditions: {filters}")
                return False

            if soft_delete:
                # Perform soft delete only if 'archive' flag is not already set
                if not getattr(existing_entry, "archive", False):
                    setattr(existing_entry, "archive", True)
                    logger.info(f"Record soft deleted with conditions: {filters}")
                else:
                    logger.info(
                        f"Record already soft deleted with conditions: {filters}"
                    )
            else:
                # Perform hard delete
                self.session.delete(existing_entry)
                logger.info(f"Record hard deleted with conditions: {filters}")

            # Commit changes if needed
            self.session.commit()
            return True

        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to delete record: {e}")
            return False

    def fetch_records_from_object(self, body):
        """
        :param body:
        :return:
        """
        final_list = []
        try:
            final_list = [
                {
                    column.name: getattr(row, column.name)
                    for column in self.table.__table__.columns
                }
                for row in body
            ]
        except Exception as e:
            status_message = "could not fetch records from object", str(e)
            logger.exception(status_message)
            raise e
        return final_list

    def fetch_record_from_object(self, body):
        """
        :param body:
        :return:
        """
        final_data = {}
        try:
            final_data = {
                column.name: getattr(body, column.name)
                for column in body.__table__.columns
            }
        except Exception as e:
            status_message = "could not fetch record from object", str(e)
            logger.exception(status_message)
            raise e
        return final_data

    def fetch_records_by_raw_query(self, raw_query: str):
        """
        Fetch multiple records using a raw SQL query and return them as a list of dictionaries.
        """
        try:
            # Execute the raw SQL query and fetch all records
            records = self.session.execute(raw_query).fetchall()

            if not records:
                return []

            # Convert each record to a dictionary using column names from the result
            return [dict(zip(record.keys(), record)) for record in records]

        except Exception as fetch_error:
            logger.error(f"Failed to execute raw query: {fetch_error}")
            return []
