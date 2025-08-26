from __future__ import annotations
from typing import List
import httpx
from bs4 import BeautifulSoup
from readability import Document
from .registry import Tool


def _fetch(url: str, timeout: int = 30) -> str:
	resp = httpx.get(url, timeout=timeout, headers={"User-Agent": "AstraCLI/0.1"})
	resp.raise_for_status()
	return resp.text


def _extract_readable(html: str, url: str | None = None) -> str:
	doc = Document(html, url=url)
	title = doc.short_title() or ""
	content = doc.summary(html_partial=True)
	soup = BeautifulSoup(content, "lxml")
	text = soup.get_text("\n")
	return (title + "\n\n" + text).strip()


def default_tools() -> List[Tool]:
	return [
		Tool(name="http_fetch", description="HTTP GET fetch raw HTML/text", parameters={"url": str, "timeout": int}, func=lambda url, timeout=30: _fetch(url, timeout)),
		Tool(name="html_readable", description="Extract readable text from HTML", parameters={"html": str, "url": str}, func=lambda html, url=None: _extract_readable(html, url)),
	]