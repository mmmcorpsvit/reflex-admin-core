from dataclasses import dataclass
from typing import Any

@dataclass
class FilterExpression:
    field: str
    operator: str  # eq, lt, gt, lte, gte, contains
    value: Any
