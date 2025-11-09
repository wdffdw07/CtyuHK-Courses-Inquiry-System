"""HTML caching utilities for scraper."""
import os
from typing import Optional


def maybe_read_cache(cache_dir: Optional[str], url: str) -> Optional[str]:
    """Try to read cached HTML for a URL.
    
    Args:
        cache_dir: directory for HTML cache
        url: URL to look up
        
    Returns:
        Cached HTML content or None if not found
    """
    if not cache_dir:
        return None
    os.makedirs(cache_dir, exist_ok=True)
    key = url.replace("https://", "").replace("http://", "").replace("/", "_")
    path = os.path.join(cache_dir, key + ".html")
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None
    return None


def write_cache(cache_dir: Optional[str], url: str, html: str) -> None:
    """Write HTML content to cache.
    
    Args:
        cache_dir: directory for HTML cache
        url: URL key
        html: HTML content to cache
    """
    if not cache_dir:
        return
    os.makedirs(cache_dir, exist_ok=True)
    key = url.replace("https://", "").replace("http://", "").replace("/", "_")
    path = os.path.join(cache_dir, key + ".html")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception:
        pass
