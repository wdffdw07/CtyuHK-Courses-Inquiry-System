"""Dependency graph visualization utilities - BACKWARD COMPATIBILITY WRAPPER.

This module is now a compatibility wrapper. The actual implementation has been
split into separate modules:
  - core.vis.common: Shared utilities (load_relations, build_graph, etc.)
  - core.vis.dependency: Dependency tree rendering
  - core.vis.roots: Roots-only graph rendering

For new code, import directly from those modules. This file re-exports
everything for backward compatibility.
"""

# Re-export all functions from new modular structure
from .common import load_relations, load_exclusions as _load_exclusions, build_graph
from .dependency import render_dependency_tree
from .roots import render_root_courses

__all__ = [
    "load_relations",
    "build_graph",
    "render_dependency_tree",
    "render_root_courses",
]
