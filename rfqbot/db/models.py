import sqlalchemy as sa
import datetime as dt
from sqlalchemy import orm
from typing import Optional
from sqlalchemy.dialects.postgresql import JSONB

class Base(orm.DeclarativeBase):
    type_annotation_map = {
        str: sa.Text,
        dict: JSONB,
        dt.datetime: sa.DateTime,
        bool: sa.Boolean,
    }

schema_name='rfq'

class RFQ(Base):
    __tablename__ = 'rfq_tbl'
    __table_args__ = {'schema': schema_name}

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    rfq_id: orm.Mapped[int] = orm.mapped_column(index=True)
    pol: orm.Mapped[Optional[str]] = orm.mapped_column()
    pod: orm.Mapped[Optional[str]] = orm.mapped_column()
    contact_names: orm.Mapped[Optional[str]] = orm.mapped_column()
    contact_numbers: orm.Mapped[Optional[str]] = orm.mapped_column()
    pickup_addresses: orm.Mapped[Optional[str]] = orm.mapped_column()
    delivery_addresses: orm.Mapped[Optional[str]] = orm.mapped_column()
    package_summary: orm.Mapped[Optional[str]] = orm.mapped_column()
    created_at: orm.Mapped[dt.datetime] = orm.mapped_column(nullable=False,server_default=sa.text("CURRENT_TIMESTAMP"))
    status: orm.Mapped[Optional[str]] = orm.mapped_column()
    reply_message: orm.Mapped[Optional[str]] = orm.mapped_column(server_default=sa.text("'IN_PROGRESS'"))

