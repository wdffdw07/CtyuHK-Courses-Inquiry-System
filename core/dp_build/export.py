"""Export utilities for major page data."""
import csv
import json
from dataclasses import asdict
from typing import List

from core.dp_build.models import MajorPage, StructureTable


def majorpage_to_dict(mp: MajorPage) -> dict:
    """Convert MajorPage to dict for JSON serialization."""
    d = asdict(mp)
    d["structure_tables"] = [asdict(t) for t in mp.structure_tables]
    return d


def save_json(objs: List[MajorPage], out_path: str) -> None:
    """Save major pages as JSON.
    
    Args:
        objs: list of MajorPage objects
        out_path: output file path
    """
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([majorpage_to_dict(o) for o in objs], f, ensure_ascii=False, indent=2)


def save_csv(objs: List[MajorPage], out_path: str) -> None:
    """Save major pages as CSV.
    
    Args:
        objs: list of MajorPage objects
        out_path: output file path
    """
    def join_list(lst: List[str]) -> str:
        return "\n".join(lst)

    def flatten_tables(tables: List[StructureTable]) -> str:
        parts = []
        for t in tables:
            parts.append(f"# {t.caption or ''}")
            if t.headers:
                parts.append(" | ".join(t.headers))
            for r in t.rows:
                parts.append(" | ".join(r))
            parts.append("")
        return "\n".join(parts).strip()

    fieldnames = [
        "url",
        "program_title",
        "program_code",
        "aims",
        "il_outcomes",
        "structure_tables",
        "remarks",
    ]
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for o in objs:
            writer.writerow({
                "url": o.url,
                "program_title": o.program_title or "",
                "program_code": o.program_code or "",
                "aims": o.aims or "",
                "il_outcomes": join_list(o.il_outcomes),
                "structure_tables": flatten_tables(o.structure_tables),
                "remarks": o.remarks or "",
            })
