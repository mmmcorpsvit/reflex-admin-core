from typing import List
from sqlalchemy import inspect
from ..core.definitions import FieldDefinition

def inspect_model_fields(model, exclude: List[str] | None = None) -> List[FieldDefinition]:
    exclude = set(exclude or [])
    mapper = inspect(model)
    fields = []
    for col in mapper.attrs:  # includes columns and relationships
        # Only expose simple column properties as fields
        try:
            if hasattr(col, "columns"):
                col0 = col.columns[0]
                name = col.key
                if name in exclude:
                    continue
                fd = FieldDefinition(
                    name=name,
                    python_type=col0.type.python_type if hasattr(col0.type, "python_type") else str,
                    nullable=col0.nullable,
                    primary_key=col0.primary_key,
                    readonly=False,
                    default=col0.default.arg if col0.default is not None else None,
                )
                fields.append(fd)
        except Exception:
            # relationships or columns with exotic types may raise; skip non-column attributes
            continue
    return fields
