from scripts.core.constants.app_constants import PSQLTableNames
from scripts.db.psql.databases import Base
from sqlalchemy import TIMESTAMP, Column, Integer, String, func


class DBModelProduction(Base):
    __tablename__ = PSQLTableNames.production_plan

    # columns
    process_order = Column(String, primary_key=True)
    site = Column(String)
    area = Column(String)
    line = Column(String)
    product = Column(String)
    sku = Column(String)
    scheduled_start_time = Column(TIMESTAMP(timezone=True))
    scheduled_end_time = Column(TIMESTAMP(timezone=True))
    start_time = Column(TIMESTAMP(timezone=True))
    end_time = Column(TIMESTAMP(timezone=True))
    order_quantity = Column(Integer)
    uom = Column(String)
    created_dt = Column(TIMESTAMP(timezone=True), default=func.now())
    modified_dt = Column(TIMESTAMP(timezone=True), default=func.now())
    planned_production_rate = Column(Integer)
    rejected_quantity = Column(Integer)
    actual_quantity_produced = Column(Integer)