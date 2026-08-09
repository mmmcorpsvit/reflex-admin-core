from dataclasses import dataclass
from typing import List
from .definitions import FieldDefinition

@dataclass
class FormDefinition:
    fields: List[FieldDefinition]
