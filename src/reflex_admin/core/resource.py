from typing import Any, List, Optional, Sequence, Type
from dataclasses import dataclass, field

from ..sqlalchemy.introspection import inspect_model_fields
from ..sqlalchemy.queries import build_list_query, count_query
from ..sqlalchemy.crud import create_object, update_object, delete_object, get_object
from ..core.definitions import FieldDefinition
from pydantic import BaseModel

@dataclass
class Resource:
    model: Any = None  # SQLAlchemy model class
    list_display: Sequence[str] = field(default_factory=list)
    search_fields: Sequence[str] = field(default_factory=list)
    readonly_fields: Sequence[str] = field(default_factory=list)
    exclude_fields: Sequence[str] = field(default_factory=list)
    create_schema: Optional[Type[BaseModel]] = None
    update_schema: Optional[Type[BaseModel]] = None

    _cached_fields: Optional[List[FieldDefinition]] = None

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
        if self.create_schema:
            validated = self.create_schema.parse_obj(payload).dict()
        else:
            validated = payload
        return create_object(session, self.model, validated)

    def update(self, session, obj_id, payload: dict):
        if self.update_schema:
            validated = self.update_schema.parse_obj(payload).dict()
        else:
            validated = payload
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
