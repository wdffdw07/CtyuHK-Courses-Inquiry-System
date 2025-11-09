"""Common utilities for graph visualization.

Shared functions for loading data and building graphs from SQLite database.
"""

from __future__ import annotations

import os
import sqlite3
from typing import Dict, Set, Tuple, List

try:
    import networkx as nx  # type: ignore
except ImportError as e:  # pragma: no cover
    raise RuntimeError("networkx is required. Install: pip install networkx matplotlib") from e


def load_relations(db_path: str) -> Tuple[Dict[str, Dict], List[Tuple[str, str]]]:
    """Load courses and prerequisite pairs from SQLite.

    Returns:
        courses: mapping code -> {title, offering_unit, credit_units}
        edges: list of (prereq -> course) pairs
    """
    if not os.path.isfile(db_path):
        raise FileNotFoundError(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT course_code, course_title, offering_unit, credit_units FROM courses")
    courses: Dict[str, Dict] = {}
    for code, title, unit, cu in cur.fetchall():
        courses[code] = {"title": title, "unit": unit, "credits": cu}
    cur.execute("SELECT prereq_code, course_code FROM prerequisites")
    edges = [(pre, course) for pre, course in cur.fetchall() if pre in courses and course in courses]
    conn.close()
    return courses, edges


def load_exclusions(db_path: str) -> Dict[str, Set[str]]:
    """Load course exclusions mapping from database.
    
    Returns:
        mapping: course_code -> set of excluded course codes
    """
    mapping: Dict[str, Set[str]] = {}
    if not os.path.isfile(db_path):
        return mapping
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT course_code, excluded_code FROM exclusions")
        for c, e in cur.fetchall():
            if not c or not e:
                continue
            mapping.setdefault(c, set()).add(e)
    except Exception:
        pass
    finally:
        conn.close()
    return mapping


def build_graph(courses: Dict[str, Dict], edges: List[Tuple[str, str]]):
    """Build a networkx directed graph from courses and edges."""
    g = nx.DiGraph()
    for code, meta in courses.items():
        g.add_node(code, **meta)
    for pre, course in edges:
        g.add_edge(pre, course)
    return g


__all__ = [
    "load_relations",
    "load_exclusions",
    "build_graph",
]
