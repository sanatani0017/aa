from __future__ import annotations
import pathlib
from typing import List
from pathspec import PathSpec
from .registry import Tool


def _load_gitignore(root: str) -> PathSpec:
	p = pathlib.Path(root) / ".gitignore"
	if not p.exists():
		return PathSpec.from_lines("gitwildmatch", [])
	return PathSpec.from_lines("gitwildmatch", p.read_text(encoding="utf-8", errors="ignore").splitlines())


def _list_repo_files(root: str) -> List[str]:
	spec = _load_gitignore(root)
	files: List[str] = []
	for p in pathlib.Path(root).rglob("*"):
		if not p.is_file():
			continue
		rel = str(p.relative_to(root))
		if spec.match_file(rel):
			continue
		files.append(str(p))
	return files


def default_tools() -> List[Tool]:
	return [
		Tool(name="repo_files", description="List repo files honoring .gitignore", parameters={"root": str}, func=lambda root: _list_repo_files(root)),
	]