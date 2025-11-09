import time
from typing import Optional
import requests

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
}

def fetch_html(url: str, *, timeout: float = 15.0, retries: int = 3, delay: float = 0.0, session: Optional[requests.Session] = None) -> str:
    sess = session or requests.Session()
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp = sess.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
            resp.raise_for_status()
            if delay:
                time.sleep(delay)
            return resp.text
        except Exception as e:
            last_exc = e
            if attempt < retries:
                time.sleep(min(1.0 * attempt, 3.0))
            else:
                raise
    raise last_exc  # type: ignore
