from typing import Any, List, Optional, Sequence, Type
from dataclasses import field

from ..sqlalchemy.introspection import inspect_model_fields, get_model_column_names
from ..sqlalchemy.queries import build_list_query, count_query
from ..sqlalchemy.crud import create_object, update_object, delete_object, get_object
from ..core.definitions import FieldDefinition
from pydantic import BaseModel


class Resource:
    """A declarative admin Resource.

    Subclass this and set `model = YourModel` and optional metadata like
    `list_display`, `search_fields`, `readonly_fields`, `exclude_fields`.

    Validation of configured fields occurs at instantiation time to fail fast.

    The caller owns the SQLAlchemy session lifecycle; Resource methods accept
    a session and never create global sessions.
    """

    model: Any = None
    list_display: Sequence[str] = []
    search_fields: Sequence[str] = []
    readonly_fields: Sequence[str] = []
    exclude_fields: Sequence[str] = []
    create_schema: Optional[Type[BaseModel]] = None
    update_schema: Optional[Type[BaseModel]] = None

    _cached_fields: Optional[List[FieldDefinition]] = None

    MAX_PAGE_SIZE = 100

    def __init__(self, *, model: Any = None):
        # Allow overriding model at instance creation
        if model is not None:
            self.model = model
        if self.model is None:
            raise ValueError("Resource must have a SQLAlchemy model assigned (class attribute or __init__ argument)")
        # validate configured fields early
        self._validate_configuration()

    def _validate_configuration(self):
        cols = set(get_model_column_names(self.model))
        for name in getattr(self, "list_display", []):
            if name not in cols:
                raise ValueError(f"Invalid list_display field: {name}")
        for name in getattr(self, "search_fields", []):
            if name not in cols:
                raise ValueError(f"Invalid search field: {name}")
        for name in getattr(self, "readonly_fields", []):
            if name not in cols:
                raise ValueError(f"Invalid readonly field: {name}")
        for name in getattr(self, "exclude_fields", []):
            if name not in cols:
                raise ValueError(f"Invalid exclude field: {name}")

    def get_fields(self) -> List[FieldDefinition]:
        if self._cached_fields is None:
            self._cached_fields = inspect_model_fields(self.model, exclude=list(self.exclude_fields))
        return self._cached_fields

    def list(
        self,
        session,
        search: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_desc: bool = False,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[list] = None,
    ):
        # validate pagination
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1 or page_size > self.MAX_PAGE_SIZE:
            raise ValueError(f"page_size must be between 1 and {self.MAX_PAGE_SIZE}")

        # validate sort_field
        if sort_field is not None:
            if sort_field not in get_model_column_names(self.model):
                raise ValueError(f"Invalid sort field: {sort_field}")

        query = build_list_query(
            session=session,
            model=self.model,
            search=search,
            search_fields=list(self.search_fields),
            sort_field=sort_field,
            sort_desc=sort_desc,
            filters=filters or [],
        )
        total = count_query(session, query)
        # pagination
        offset = (page - 1) * page_size
        items = query.limit(page_size).offset(offset).all()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def create(self, session, payload: dict):
        # Validate with pydantic if schema provided
        if self.create_schema:
            validated = self.create_schema.parse_obj(payload).dict()
        else:
            validated = dict(payload)
        # strip excluded and readonly and PK fields
        pk_names = [c.name for c in self.model.__table__.primary_key.columns]
        for key in list(validated.keys()):
            if key in getattr(self, "exclude_fields", []):
                validated.pop(key, None)
            if key in getattr(self, "readonly_fields", []):
                validated.pop(key, None)
            if key in pk_names:
                validated.pop(key, None)
        return create_object(session, self.model, validated)

    def update(self, session, obj_id, payload: dict):
        # Validate
        if self.update_schema:
            validated = self.update_schema.parse_obj(payload).dict()
        else:
            validated = dict(payload)
        # prevent updates to readonly and PK
        pk_names = [c.name for c in self.model.__table__.primary_key.columns]
        for key in list(validated.keys()):
            if key in getattr(self, "readonly_fields", []):
                validated.pop(key, None)
            if key in pk_names:
                validated.pop(key, None)
        obj = get_object(session, self.model, obj_id)
        if obj is None:
            raise ValueError("Not found")
        return update_object(session, obj, validated)

    def delete(self, session, obj_id):
        obj = get_object(session, self.model, obj_id)
        if obj is None:
            raise ValueError("Not found")
        return delete_object(session, obj)

    def get(self, session, obj_id):
        return get_object(session, self.model, obj_id)
