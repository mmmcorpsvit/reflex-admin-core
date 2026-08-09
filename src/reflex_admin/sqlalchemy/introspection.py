from typing import List
from sqlalchemy import inspect, String, Text, Integer, Float, Numeric, Boolean, Date, DateTime
from ..core.definitions import FieldDefinition

TYPE_MAPPING = [
    (String, "string"),
    (Text, "text"),
    (Integer, "integer"),
    (Float, "float"),
    (Numeric, "numeric"),
    (Boolean, "boolean"),
    (Date, "date"),
    (DateTime, "datetime"),
]


def _map_type(coltype):
    for t, name in TYPE_MAPPING:
        try:
            if isinstance(coltype, t):
                return name
        except Exception:
            continue
    # fallback to python_type
    try:
        py = getattr(coltype, "python_type", None)
        if py is str:
            return "string"
        if py is int:
            return "integer"
        if py is float:
            return "float"
    except Exception:
        pass
    return "unknown"


def get_model_column_names(model) -> List[str]:
    mapper = inspect(model)
    return list(mapper.columns.keys())


def inspect_model_fields(model, exclude: List[str] | None = None) -> List[FieldDefinition]:
    exclude = set(exclude or [])
    mapper = inspect(model)
    fields: List[FieldDefinition] = []
    for col in mapper.attrs:
        try:
            if hasattr(col, "columns"):
                col0 = col.columns[0]
                name = col.key
                if name in exclude:
                    continue
                type_name = _map_type(col0.type)
                fd = FieldDefinition(
                    name=name,
                    python_type=col0.type.python_type if hasattr(col0.type, "python_type") else str,
                    type=type_name,
                    nullable=col0.nullable,
                    primary_key=col0.primary_key,
                    readonly=False,
                    default=col0.default.arg if col0.default is not None else None,
                )
                # mark foreign keys
                try:
                    fks = list(col0.foreign_keys)
                    if fks:
                        fd.type = fd.type or "foreignkey"
                except Exception:
                    pass
                fields.append(fd)
        except Exception:
            continue
    return fields
