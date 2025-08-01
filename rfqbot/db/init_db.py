from .db_config import ConfigDB
from . import models
import sqlalchemy as sa
from sqlalchemy import orm

engine=sa.create_engine(ConfigDB.db_url())

def init_db():
    with orm.Session(engine) as session:
        with session.begin():
            session.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS {models.schema_name}'))
    models.Base.metadata.create_all(engine)


def insert_rfq(columns:dict):
    with orm.Session(engine) as session:
        with session.begin():
            new_rfq = models.RFQ(
                rfq_id=columns.get('rfq_id'),
                pol=columns.get('pol'),
                pod=columns.get('pod'),
                contact_names=columns.get('contact_names'),
                contact_numbers=columns.get('contact_numbers'),
                pickup_addresses=columns.get('pickup_addresses'),
                delivery_addresses=columns.get('delivery_addresses')
            )
            session.add(new_rfq)
            print(f'Inserted new RFQ {new_rfq.rfq_id}')

def fetch_rfq(rfq_id:int) -> models.RFQ:
    with orm.Session(engine) as session:
        with session.begin():
            stmt = sa.select(models.RFQ).where(models.RFQ.rfq_id == rfq_id).limit(1)
            res = session.execute(stmt).scalar_one_or_none()
            return res
