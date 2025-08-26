from __future__ import annotations
from typing import List, Set
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from .registry import Tool


def _crawl(url: str, max_pages: int = 10, timeout: int = 15) -> List[str]:
	seen: Set[str] = set()
	results: List[str] = []
	resp = httpx.get(url, timeout=timeout, headers={"User-Agent": "AstraCLI/0.1"})
	resp.raise_for_status()
	soup = BeautifulSoup(resp.text, "lxml")
	base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
	for a in soup.find_all("a"):
		href = a.get("href")
		if not href:
			continue
		u = urljoin(url, href)
		if not u.startswith(base):
			continue
		if u in seen:
			continue
		seen.add(u)
		results.append(u)
		if len(results) >= max_pages:
			break
	return results


def default_tools() -> List[Tool]:
	return [
		Tool(name="crawl_links", description="Same-domain depth-1 link collector", parameters={"url": str, "max_pages": int, "timeout": int}, func=lambda url, max_pages=10, timeout=15: _crawl(url, max_pages, timeout)),
	]