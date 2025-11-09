# Visualization package for curriculum dependency graphs

# Re-export from new modular structure for backward compatibility
from .common import load_relations, load_exclusions, build_graph
from .dependency import render_dependency_tree
from .roots import render_root_courses

__all__ = [
    "load_relations",
    "load_exclusions", 
    "build_graph",
    "render_dependency_tree",
    "render_root_courses",
]
