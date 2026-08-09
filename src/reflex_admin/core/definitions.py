from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class FieldDefinition:
    name: str
    python_type: Any
    type: str = "unknown"
    nullable: bool = True
    primary_key: bool = False
    readonly: bool = False
    default: Optional[Any] = None
