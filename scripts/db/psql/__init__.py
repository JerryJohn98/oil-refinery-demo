import psycopg2
from psycopg2.errorcodes import CARDINALITY_VIOLATION, UNDEFINED_COLUMN
from scripts.config.app_configurations import DBConf
from scripts.logging.logging import logger
from sqlalchemy import Column, MetaData, Table, exc
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.schema import DDL


class TableDDL:
    def __init__(self, engine_ref, table_name):
        self.engine_ref = engine_ref
        self.table_name = table_name

    def create_model(self, data_types: dict):
        metadata = MetaData()
        table = Table(self.table_name, metadata, schema=DBConf.pg_schema)

        [
            table.append_column(Column(column_name, d_type[0], primary_key=d_type[1]))
            for column_name, d_type in data_types.items()
        ]

        return table

    def create_new_table(self, data_types: dict):
        metadata = MetaData()
        table = Table(self.table_name, metadata, schema=DBConf.pg_schema)

        [
            table.append_column(Column(column_name, d_type[0], primary_key=d_type[1]))
            for column_name, d_type in data_types.items()
        ]

        metadata.create_all(self.engine_ref)

    def insert_data(self, data_df, data_types, primary_keys):
        table_model = self.create_model(data_types)
        try:
            self.upsert_to_table(table_model, primary_keys, data_df)
        except (exc.SQLAlchemyError, psycopg2.Error) as e:
            if e.orig.pgcode == UNDEFINED_COLUMN:
                self.alter_add_column(data_types)
                self.upsert_to_table(table_model, primary_keys, data_df)
        except Exception as e:
            logger.exception(e)

    def upsert_to_table(self, table_model, primary_keys, data_df):
        try:
            insrt_vals = data_df.to_dict(orient="records")
            insert_ = insert(table_model).values(insrt_vals)

            index_ele = [getattr(table_model.columns, x) for x in primary_keys]
            set_vals = {
                x: getattr(insert_.excluded, x)
                for x in data_df
                if x not in primary_keys
            }

            update_ = insert_.on_conflict_do_update(
                index_elements=index_ele, set_=set_vals
            )
            self.engine_ref.execute(update_)
        except (exc.SQLAlchemyError, psycopg2.Error) as e:
            if e.orig.pgcode == CARDINALITY_VIOLATION:
                logger.error("Primary key values not unique")
            else:
                logger.error(f"Other Errors: {str(e)}")
        except Exception as e:
            logger.exception(e)
            raise

    def alter_add_column(self, data_types):
        try:
            metadata = MetaData(bind=self.engine_ref)
            existing_table = Table(
                self.table_name, metadata, autoload=True, schema=DBConf.pg_schema
            )
            existing_columns = existing_table.columns.keys()
            missing_columns = set(data_types.keys()) - set(existing_columns)
            for col in missing_columns:
                column = Column(col, data_types[col][0], primary_key=data_types[col][1])
                alter_table_stmt = DDL(
                    f"ALTER TABLE {self.table_name} ADD COLUMN {column.compile(metadata.bind)} "
                    f"{column.type.compile(self.engine_ref.dialect)}"
                )
                with self.engine_ref.connect() as connection:
                    connection.execute(alter_table_stmt)
        except Exception as e:
            logger.exception(e)
