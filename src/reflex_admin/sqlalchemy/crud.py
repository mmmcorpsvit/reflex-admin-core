from typing import Any, Dict
from sqlalchemy.orm import Session

def create_object(session: Session, model, data: Dict):
    obj = model(**data)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def get_object(session: Session, model, obj_id):
    # attempt to find by primary key column name "id" first, fallback to PKs
    pk_cols = [c.name for c in model.__table__.primary_key.columns]
    if "id" in pk_cols:
        return session.query(model).get(obj_id)
    # otherwise assume single PK and use positional indexing
    if len(pk_cols) == 1:
        return session.query(model).get(obj_id)
    # composite key not supported in POC
    raise ValueError("Composite PK not supported in POC")

def update_object(session: Session, obj, data: Dict):
    for k, v in data.items():
        if hasattr(obj, k):
            setattr(obj, k, v)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def delete_object(session: Session, obj):
    session.delete(obj)
    session.commit()
    return True
