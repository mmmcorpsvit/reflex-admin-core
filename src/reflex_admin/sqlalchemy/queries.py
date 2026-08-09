from typing import List, Optional
from sqlalchemy import or_, func, inspect, asc, desc
from sqlalchemy.orm import Session
from .introspection import inspect_model_fields, get_model_column_names
from ..core.filters import FilterExpression
from sqlalchemy.sql import selectable

ALLOWED_OPERATORS = {"eq", "lt", "gt", "lte", "gte", "contains"}


def _validate_field(model, field: str) -> bool:
    cols = get_model_column_names(model)
    return field in cols


def _is_text_column(model, field: str) -> bool:
    mapper = inspect(model)
    col = mapper.columns.get(field)
    if col is None:
        return False
    t = col.type
    # simple heuristic: string/text types or python_type == str
    from sqlalchemy import String, Text

    if isinstance(t, (String, Text)):
        return True
    try:
        if getattr(t, "python_type", None) is str:
            return True
    except Exception:
        pass
    return False


def apply_filters(query, model, filters: List[FilterExpression]):
    for f in filters:
        if not _validate_field(model, f.field):
            raise ValueError(f"Invalid filter field: {f.field}")
        col = getattr(model, f.field)
        op = f.operator
        if op not in ALLOWED_OPERATORS:
            raise ValueError(f"Invalid operator: {op}")
        if op == "eq":
            query = query.filter(col == f.value)
        elif op == "lt":
            query = query.filter(col < f.value)
        elif op == "gt":
            query = query.filter(col > f.value)
        elif op == "lte":
            query = query.filter(col <= f.value)
        elif op == "gte":
            query = query.filter(col >= f.value)
        elif op == "contains":
            # only allow contains on text-like columns
            if not _is_text_column(model, f.field):
                raise ValueError(f"Operator 'contains' not supported for field: {f.field}")
            query = query.filter(col.ilike(f"%{f.value}%"))
    return query


def apply_search(query, model, search_term: Optional[str], search_fields: List[str]):
    if not search_term:
        return query
    if not search_fields:
        return query
    mapper = inspect(model)
    clauses = []
    for field in search_fields:
        if field not in mapper.columns.keys():
            raise ValueError(f"Invalid search field: {field}")
        if not _is_text_column(model, field):
            # skip non-text fields from generic search
            continue
        col = getattr(model, field)
        clauses.append(col.ilike(f"%{search_term}%"))
    if clauses:
        query = query.filter(or_(*clauses))
    return query


def apply_sort(query, model, sort_field: Optional[str], sort_desc: bool = False):
    if not sort_field:
        return query
    if not _validate_field(model, sort_field):
        raise ValueError("Invalid sort field")
    col = getattr(model, sort_field)
    # stable sort: tie-breaker on primary key(s) ascending
    mapper = inspect(model)
    pk_cols = list(mapper.primary_key)
    orderers = [desc(col) if sort_desc else asc(col)]
    for pk in pk_cols:
        orderers.append(asc(pk))
    return query.order_by(*orderers)


def build_list_query(session: Session, model, search: Optional[str], search_fields: List[str], sort_field: Optional[str], sort_desc: bool, filters: List[FilterExpression]):
    q = session.query(model)
    q = apply_filters(q, model, filters)
    q = apply_search(q, model, search, search_fields)
    q = apply_sort(q, model, sort_field, sort_desc)
    return q


def count_query(session: Session, query):
    # Use a subquery to count filtered rows reliably
    subq = query.subquery()
    count_q = session.query(func.count()).select_from(subq)
    return int(count_q.scalar() or 0)
