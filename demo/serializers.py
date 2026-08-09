from datetime import datetime

def serialize_user(u):
    return {
        "id": getattr(u, "id", None),
        "email": getattr(u, "email", None),
        "name": getattr(u, "name", None),
        "active": bool(getattr(u, "active", False)),
        "created_at": getattr(u, "created_at").isoformat() if getattr(u, "created_at", None) else None,
    }
