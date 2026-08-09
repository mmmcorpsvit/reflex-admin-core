from typing import List, Optional
from sqlalchemy import or_, func, inspect, asc, desc
from sqlalchemy.orm import Session
from .introspection import inspect_model_fields
from ..core.filters import FilterExpression

ALLOWED_OPERATORS = {"eq", "lt", "gt", "lte", "gte", "contains"}

def _validate_field(model, field: str) -> bool:
    mapper = inspect(model)
    return field in mapper.columns.keys()

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
            query = query.filter(col.ilike(f"%{f.value}%"))
    return query

def apply_search(query, model, search_term: Optional[str], search_fields: List[str]):
    if not search_term or not search_fields:
        return query
    mapper = inspect(model)
    clauses = []
    for field in search_fields:
        if field not in mapper.columns.keys():
            continue
        col = getattr(model, field)
        # only use text-like search for textual columns
        try:
            clauses.append(col.ilike(f"%{search_term}%"))
        except Exception:
            continue
    if clauses:
        query = query.filter(or_(*clauses))
    return query

def apply_sort(query, model, sort_field: Optional[str], sort_desc: bool = False):
    if not sort_field:
        return query
    if not _validate_field(model, sort_field):
        raise ValueError("Invalid sort field")
    col = getattr(model, sort_field)
    return query.order_by(desc(col) if sort_desc else asc(col))

def build_list_query(session: Session, model, search: Optional[str], search_fields: List[str], sort_field: Optional[str], sort_desc: bool, filters: List[FilterExpression]):
    q = session.query(model)
    q = apply_filters(q, model, filters)
    q = apply_search(q, model, search, search_fields)
    q = apply_sort(q, model, sort_field, sort_desc)
    return q

def count_query(session: Session, query):
    # query comes from session.query(model) with filters applied
    count_q = query.statement.with_only_columns([func.count()]).order_by(None)
    return int(session.execute(count_q).scalar())
