from __future__ import annotations
import os
import pathlib
from typing import Any, Dict, List
from .registry import Tool


def _read_file(path: str) -> str:
	p = pathlib.Path(path)
	return p.read_text(encoding="utf-8", errors="ignore")


def _write_file(path: str, content: str, overwrite: bool = True) -> str:
	p = pathlib.Path(path)
	p.parent.mkdir(parents=True, exist_ok=True)
	if not overwrite and p.exists():
		raise FileExistsError(str(p))
	p.write_text(content, encoding="utf-8")
	return str(p)


def _list_dir(path: str) -> List[str]:
	return sorted([str(p) for p in pathlib.Path(path).iterdir()])


def default_tools() -> List[Tool]:
	return [
		Tool(name="fs_read", description="Read a text file", parameters={"path": str}, func=lambda path: _read_file(path)),
		Tool(name="fs_write", description="Write a text file", parameters={"path": str, "content": str, "overwrite": bool}, func=lambda path, content, overwrite=True: _write_file(path, content, overwrite)),
		Tool(name="fs_list", description="List directory entries", parameters={"path": str}, func=lambda path: _list_dir(path)),
	]