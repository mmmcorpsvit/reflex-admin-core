from typing import List
from .definitions import FieldDefinition

def fields_to_names(fields: List[FieldDefinition]):
    return [f.name for f in fields]
