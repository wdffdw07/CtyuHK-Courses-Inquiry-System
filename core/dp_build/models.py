from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class StructureTable:
    caption: Optional[str]
    headers: List[str]
    rows: List[List[str]]

@dataclass
class MajorPage:
    url: str
    program_title: Optional[str]
    program_code: Optional[str]
    aims: Optional[str]
    il_outcomes: List[str]
    structure_tables: List[StructureTable]
    remarks: Optional[str]
    courses: List[Dict[str, Any]]
