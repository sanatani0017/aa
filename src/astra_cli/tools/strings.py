from __future__ import annotations
from typing import List
from .registry import Tool


def _replace(text: str, old: str, new: str) -> str:
	return text.replace(old, new)


def _split(text: str, sep: str = "\n") -> List[str]:
	return text.split(sep)


def default_tools() -> List[Tool]:
	return [
		Tool(name="str_replace", description="Replace substring", parameters={"text": str, "old": str, "new": str}, func=lambda text, old, new: _replace(text, old, new)),
		Tool(name="str_split", description="Split text", parameters={"text": str, "sep": str}, func=lambda text, sep="\n": _split(text, sep)),
	]