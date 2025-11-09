"""Scraping orchestration for major pages."""
import os
import sys
from typing import List, Optional

import requests

from core.scraper.http import fetch_html
from core.scraper.cache import maybe_read_cache, write_cache
from core.dp_build.parsers import parse_major_page
from core.dp_build.models import MajorPage


def scrape_major_pages(
    urls: List[str],
    *,
    delay: float = 0.0,
    timeout: float = 15.0,
    retries: int = 3,
    verbose: bool = False,
    include_courses: bool = False,
    concurrency: int = 1,
    cache_dir: Optional[str] = None
) -> List[MajorPage]:
    """Scrape one or more major curriculum pages.
    
    Args:
        urls: list of major page URLs to scrape
        delay: delay between requests
        timeout: request timeout
        retries: number of retries for failed requests
        verbose: print progress messages
        include_courses: also fetch course detail pages
        concurrency: number of concurrent workers for course fetching
        cache_dir: directory for HTML cache
        
    Returns:
        List of MajorPage objects
    """
    session = requests.Session()
    results: List[MajorPage] = []
    
    for i, u in enumerate(urls, 1):
        if verbose:
            print(f"[{i}/{len(urls)}] Fetching {u}")
        
        try:
            html = maybe_read_cache(cache_dir, u)
            if html is None:
                html = fetch_html(u, timeout=timeout, retries=retries, delay=delay, session=session)
                write_cache(cache_dir, u, html)
            
            mp = parse_major_page(
                u,
                html,
                include_courses=include_courses,
                session=session,
                delay=delay,
                timeout=timeout,
                retries=retries,
                verbose=verbose,
                concurrency=concurrency,
                cache_dir=cache_dir,
            )
            results.append(mp)
            
            if verbose:
                print(f"  -> {mp.program_title or 'N/A'} tables={len(mp.structure_tables)} courses={len(mp.courses)}")
        except Exception as e:
            print(f"Error {u}: {e}", file=sys.stderr)
    
    return results
