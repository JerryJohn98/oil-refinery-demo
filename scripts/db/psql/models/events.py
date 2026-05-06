from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from scripts.core.constants.app_constants import PSQLTableNames
from scripts.db.psql.databases import Base


class DBModelEventCategories(Base):
    __tablename__ = PSQLTableNames.event_categories

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String)
    description = Column(Text)
    created_by = Column(String)
    created_dt = Column(TIMESTAMP(timezone=True))
    modified_by = Column(String)
    modified_dt = Column(TIMESTAMP(timezone=True))
    archive = Column(Boolean, default=False)


class DBModelEventSubCategory(Base):
    __tablename__ = PSQLTableNames.event_sub_category

    sub_category_id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String)
    description = Column(Text)
    category_id = Column(
        Integer, ForeignKey(f"{PSQLTableNames.event_categories}.category_id")
    )
    level = Column(String)
    created_by = Column(String)
    created_dt = Column(TIMESTAMP(timezone=True))
    modified_by = Column(String)
    modified_dt = Column(TIMESTAMP(timezone=True))
    archive = Column(Boolean, default=False)

    event_category_label = relationship(
        "DBModelEventCategories",
        backref=PSQLTableNames.event_sub_category,
        lazy="joined",
    )


class DBModelReasonCode(Base):
    __tablename__ = PSQLTableNames.reason_code

    reason_code = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String)
    description = Column(Text)
    category_id = Column(
        Integer, ForeignKey(f"{PSQLTableNames.event_categories}.category_id")
    )
    sub_category_id = Column(
        Integer, ForeignKey(f"{PSQLTableNames.event_sub_category}.sub_category_id")
    )
    created_by = Column(String)
    created_dt = Column(TIMESTAMP(timezone=True))
    modified_by = Column(String)
    modified_dt = Column(TIMESTAMP(timezone=True))
    archive = Column(Boolean, default=False)

    event_category_label = relationship(
        "DBModelEventCategories", backref=PSQLTableNames.reason_code, lazy="joined"
    )
    event_sub_category_label = relationship(
        "DBModelEventSubCategory", backref=PSQLTableNames.reason_code, lazy="joined"
    )


class DBModelEvents(Base):
    __tablename__ = PSQLTableNames.events

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    event_category = Column(
        Integer, ForeignKey(f"{PSQLTableNames.event_categories}.category_id")
    )
    event_sub_category = Column(
        Integer, ForeignKey(f"{PSQLTableNames.event_sub_category}.sub_category_id")
    )
    reason_code = Column(
        Integer, ForeignKey(f"{PSQLTableNames.reason_code}.reason_code"), nullable=True
    )
    site = Column(String)
    area = Column(String)
    line = Column(String)
    equipment = Column(String, nullable=True)
    start_time = Column(TIMESTAMP(timezone=True))
    end_time = Column(TIMESTAMP(timezone=True), nullable=True)
    event_type = Column(String)
    record_type = Column(String)
    created_by = Column(String)
    created_dt = Column(TIMESTAMP(timezone=True))
    modified_by = Column(String)
    modified_dt = Column(TIMESTAMP(timezone=True))
    archive = Column(Boolean, default=False)

    # Relationship to fetch the label from event_categories
    event_category_label = relationship(
        "DBModelEventCategories", backref=PSQLTableNames.events, lazy="joined"
    )
    event_sub_category_label = relationship(
        "DBModelEventSubCategory", backref=PSQLTableNames.events, lazy="joined"
    )
    reason_code_label = relationship(
        "DBModelReasonCode", backref=PSQLTableNames.events, lazy="joined"
    )
