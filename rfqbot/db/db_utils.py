from .db_config import ConfigDB
from . import models
import sqlalchemy as sa
from sqlalchemy import orm
import datetime as dt
import pytz

IST = pytz.timezone('Asia/Kolkata')

engine=sa.create_engine(ConfigDB.db_url())

def normalize_rfq_input(data: dict) -> dict:
    def clean(value):
        if isinstance(value, list):
            return ", ".join(str(v) for v in value if v) if value else None
        return value
    return {k: clean(v) for k, v in data.items()}

def insert_rfq(columns:dict) -> int:
    columns = normalize_rfq_input(columns)
    with orm.Session(engine) as session:
        with session.begin():
            new_rfq = models.RFQ(
                pol=columns.get('pol'),
                pod=columns.get('pod'),
                contact_names=columns.get('contact_names'),
                contact_numbers=columns.get('contact_numbers'),
                pickup_addresses=columns.get('pickup_addresses'),
                delivery_addresses=columns.get('delivery_addresses'),
                created_at=columns.get('created_at') or dt.datetime.now(dt.UTC),
                email=columns.get('email')
            )
            session.add(new_rfq)
        print(f'Inserted new RFQ id {new_rfq.rfq_id}')
        return new_rfq.rfq_id

def fetch_rfq(rfq_id: int) -> dict | None:
    with orm.Session(engine) as session:
        stmt = sa.select(models.RFQ).where(models.RFQ.rfq_id == rfq_id).limit(1)
        res = session.scalar(stmt)
        if res:
            result = {col.name: getattr(res, col.name) for col in models.RFQ.__table__.columns}
            if result.get("created_at"):
                ist = result['created_at'].replace(tzinfo=pytz.utc).astimezone(IST)
                result["created_at"] = ist.strftime("%Y-%m-%d %H:%M:%S")
            return result
        print('No RFQ found')
        return None

def update_rfq(updates:dict) -> dict | None:
    updates = normalize_rfq_input(updates)
    with orm.Session(engine) as session:
        with session.begin():
            rfq_id = updates.get('rfq_id')
            stmt = sa.select(models.RFQ).where(models.RFQ.rfq_id == rfq_id).limit(1)
            existing_rfq = session.scalar(stmt)
            if not existing_rfq:
                print(f'RFQ {rfq_id} does not exist')
                return None
            for key,value in updates.items():
                if hasattr(existing_rfq, key):
                    setattr(existing_rfq, key, value)
            print(f"✅ Updated RFQ {updates.get('rfq_id')} with fields: {list(updates.keys())}")
        return updates

