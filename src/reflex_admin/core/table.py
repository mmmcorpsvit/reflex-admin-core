from dataclasses import dataclass
from typing import List

@dataclass
class ColumnDef:
    name: str
    label: str | None = None
    sortable: bool = True

@dataclass
class TableDefinition:
    columns: List[ColumnDef]
    page: int = 1
    page_size: int = 20
