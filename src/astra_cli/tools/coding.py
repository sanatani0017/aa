from __future__ import annotations
import re
import pathlib
from typing import List, Dict
from .registry import Tool


def _grep(path: str, pattern: str, ignore_case: bool = False) -> List[Dict[str, str]]:
	flags = re.IGNORECASE if ignore_case else 0
	results: List[Dict[str, str]] = []
	for p in pathlib.Path(path).rglob("*"):
		if not p.is_file():
			continue
		try:
			text = p.read_text(encoding="utf-8", errors="ignore")
		except Exception:
			continue
		for i, line in enumerate(text.splitlines(), start=1):
			if re.search(pattern, line, flags=flags):
				results.append({"file": str(p), "line": str(i), "text": line})
	return results


def _apply_edit(file: str, old: str, new: str) -> int:
	p = pathlib.Path(file)
	text = p.read_text(encoding="utf-8", errors="ignore")
	count = text.count(old)
	if count == 0:
		return 0
	text = text.replace(old, new)
	p.write_text(text, encoding="utf-8")
	return count


def default_tools() -> List[Tool]:
	return [
		Tool(name="code_grep", description="Regex search in tree", parameters={"path": str, "pattern": str, "ignore_case": bool}, func=lambda path, pattern, ignore_case=False: _grep(path, pattern, ignore_case)),
		Tool(name="code_apply_edit", description="Replace substring in file (all occurrences)", parameters={"file": str, "old": str, "new": str}, func=lambda file, old, new: _apply_edit(file, old, new)),
	]