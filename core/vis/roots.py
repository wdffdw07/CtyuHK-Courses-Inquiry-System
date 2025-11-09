"""Roots-only graph visualization.

Renders courses that have no prerequisites and no dependents (terminal courses).
"""

from __future__ import annotations

import os
from typing import Dict, Tuple, List

try:
    import networkx as nx  # type: ignore
    import matplotlib.pyplot as plt  # type: ignore
    import matplotlib.cm as cm  # type: ignore
except ImportError as e:  # pragma: no cover
    raise RuntimeError("networkx and matplotlib are required. Install: pip install networkx matplotlib") from e

from .common import load_relations, build_graph


def render_root_courses(
    db_path: str,
    out_path: str,
    truncate_title: int = 40,
    color_by_unit: bool = True,
    max_per_row: int = 8,
) -> str:
    """Render courses that have no prerequisites and no dependents.

    Include only nodes with in-degree == 0 and out-degree == 0.
    Labels show prerequisite status per node: "Prereq: None" or a short list of codes.
    
    Args:
        db_path: path to SQLite DB
        out_path: output image path (.png recommended)
        truncate_title: truncate course title to this length
        color_by_unit: color nodes by offering unit
        max_per_row: maximum number of nodes per row in grid layout
        
    Returns:
        Path to written image file.
    """
    courses, edges = load_relations(db_path)
    g = build_graph(courses, edges)
    
    # Select nodes that have NO prerequisites and NO dependents
    roots = [n for n in g.nodes if g.in_degree(n) == 0 and g.out_degree(n) == 0]
    
    # Build a simple grid layout
    rows: List[List[str]] = []
    roots_sorted = sorted(roots)
    for i in range(0, len(roots_sorted), max_per_row):
        rows.append(roots_sorted[i:i + max_per_row])
    total_rows = max(1, len(rows))
    pos: Dict[str, Tuple[float, float]] = {}
    for ridx, row in enumerate(rows):
        y = (ridx / (total_rows - 1)) if total_rows > 1 else 0.5
        count = len(row)
        for i, node in enumerate(row):
            x = 0.05 + 0.9 * (i / max(1, count - 1)) if count > 1 else 0.5
            pos[node] = (x, y)
    
    # Labels
    def _short(s: str) -> str:
        s = (s or '').strip()
        return s if len(s) <= truncate_title else s[:truncate_title - 1] + '…'
    
    # Build labels with prerequisite summary from the graph
    # Compute prereq codes by incoming edges
    in_prereqs: Dict[str, List[str]] = {n: [] for n in roots}
    for pre, course in g.edges:
        if course in in_prereqs:
            in_prereqs[course].append(pre)
    
    labels = {}
    for n in roots:
        prereqs = sorted(set(in_prereqs.get(n, [])))
        if prereqs:
            # show up to 5 prereq codes
            text = ", ".join(prereqs[:5])
            if len(prereqs) > 5:
                text += f" (+{len(prereqs)-5})"
            pre_line = f"Prereq: {text}"
        else:
            pre_line = "Prereq: None"
        labels[n] = f"{n}\n{_short(g.nodes[n].get('title') or '')}\n{pre_line}"
    
    plt.figure(figsize=(min(20, 2 + 1.1 * max_per_row), min(12, 2 + 0.8 * total_rows)))
    
    if color_by_unit:
        units = [(g.nodes[n].get('unit') or '') for n in roots]
        uniq = {u: i for i, u in enumerate(sorted(set(units)))}
        cmap = cm.get_cmap('tab20', max(1, len(uniq)))
        colors = [cmap(uniq.get(u, 0)) for u in units]
        nx.draw_networkx_nodes(g, pos, nodelist=roots, node_size=650, node_color=colors, alpha=0.9)
    else:
        nx.draw_networkx_nodes(g, pos, nodelist=roots, node_size=650, node_color='#4c72b0', alpha=0.85)
    
    nx.draw_networkx_labels(g, pos, labels=labels, font_size=8)
    plt.title(f"Courses With No Prereqs And No Dependents (Count={len(roots)})")
    plt.axis('off')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


__all__ = [
    "render_root_courses",
]
