"""Configuration utilities for the CityU curriculum tool.

负责配置文件的读取，保持主 CLI 更轻量。

Functions:
    load_config(path: str | None) -> dict
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict

try:  # Python 3.11+
    import tomllib  # type: ignore
except Exception:  # pragma: no cover
    tomllib = None  # type: ignore


 # template content moved to config/cityu.toml per user request


def load_config(path: Optional[str]) -> Dict:
    """Load a TOML config file.

    If path is None, try default config/cityu.toml.
    Returns a dict or empty dict if not found / parse failed.
    """
    if path:
        cfg_path = Path(path)
    else:
        cfg_path = Path(__file__).parent.parent / "config" / "cityu.toml"
    if not cfg_path.exists():
        return {}
    if tomllib is None:
        return {}
    try:
        with open(cfg_path, "rb") as f:
            data = tomllib.load(f)
        return data or {}
    except Exception:
        return {}


__all__ = ["load_config"]
