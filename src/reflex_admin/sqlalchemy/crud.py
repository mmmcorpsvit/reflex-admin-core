from typing import Any, Dict
from sqlalchemy.orm import Session

def create_object(session: Session, model, data: Dict):
    try:
        obj = model(**data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except Exception:
        session.rollback()
        raise


def get_object(session: Session, model, obj_id):
    # prefer session.get for SQLAlchemy 1.4+
    try:
        return session.get(model, obj_id)
    except Exception:
        # fallback
        return session.query(model).get(obj_id)


def update_object(session: Session, obj, data: Dict):
    try:
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except Exception:
        session.rollback()
        raise


def delete_object(session: Session, obj):
    try:
        session.delete(obj)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
