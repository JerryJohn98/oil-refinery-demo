import os

from fastapi import Request
from scripts.config.app_configurations import DBConf
from scripts.utils.db_name_util import get_db_name
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.schema import CreateSchema
from sqlalchemy_utils import create_database, database_exists

Base = declarative_base()


def get_assistant_db(request_data: Request, db_name: str = DBConf.ASSISTANT_DB):
    project_id = request_data.cookies.get(
        "projectId", request_data.cookies.get("project_id")
    )
    postgres_uri = DBConf.ASSISTANT_DB_URI
    postgres_uri = f"{postgres_uri}/{db_name}"
    db_name = os.path.basename(postgres_uri)
    db = (
        get_db_name(project_id=project_id, database=db_name)
        if not DBConf.pg_remove_prefix
        else db_name
    )
    engine = create_engine(
        f"{os.path.dirname(postgres_uri)}/{db}",
        pool_size=int(os.getenv("PG_POOL_SIZE")),
        poolclass=QueuePool,
        pool_timeout=int(os.getenv("PG_TIMEOUT", default=30)),
        max_overflow=int(os.getenv("PG_MAX_OVERFLOW")),
    )
    if not database_exists(engine.url):
        create_database(engine.url)
    inspector = Inspector.from_engine(engine)
    if DBConf.pg_schema not in inspector.get_schema_names():
        engine.execute(CreateSchema(DBConf.pg_schema, quote=True))
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = session_local()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()

def get_unified_model_db(request_data: Request):
    yield from get_assistant_db(
        request_data=request_data, db_name=DBConf.UNIFIED_MODEL_DB
    )


def get_event_db(request_data: Request):
    yield from get_assistant_db(
        request_data=request_data, db_name=DBConf.ILENS_EVENT_DB
    )

def get_ilens_oee_db(request_data: Request):
    yield from get_assistant_db(
        request_data=request_data, db_name=DBConf.ILENS_OEE_DB
    )

def get_shift_planning_db(request_data: Request):
    yield from get_assistant_db(
        request_data=request_data, db_name=DBConf.SHIFT_PLANNING_DB
    )