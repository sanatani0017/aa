import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from .logging import logger


@dataclass
class Tool:
	name: str
	desc: str
	call: Callable[..., Any]


class ToolRegistry:
	def __init__(self) -> None:
		self._tools: Dict[str, Tool] = {}

	def register(self, tool: Tool) -> None:
		self._tools[tool.name] = tool
		logger.info(f"Registered tool: {tool.name}")

	def get(self, name: str) -> Tool:
		return self._tools[name]

	def list(self) -> List[str]:
		return sorted(self._tools.keys())


def tool_fs_read(path: str, max_bytes: int = 200_000) -> str:
	if not os.path.exists(path):
		return f"ERROR: path not found: {path}"
	with open(path, "rb") as f:
		data = f.read(max_bytes)
	return data.decode("utf-8", errors="replace")


def tool_fs_write(path: str, content: str) -> str:
	os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		f.write(content)
	return f"WROTE:{path}:{len(content)}"


def tool_fs_copy(src: str, dst: str) -> str:
	shutil.copy2(src, dst)
	return f"COPIED:{src}->{dst}"


def tool_shell(cmd: str, cwd: Optional[str] = None, timeout: int = 120) -> str:
	try:
		out = subprocess.check_output(cmd, shell=True, cwd=cwd, stderr=subprocess.STDOUT, timeout=timeout)
		return out.decode("utf-8", errors="replace")
	except subprocess.CalledProcessError as e:
		return f"ERROR({e.returncode}): {e.output.decode('utf-8', errors='replace')[:4000]}"


def tool_web_fetch(url: str, max_chars: int = 200_000) -> str:
	resp = requests.get(url, timeout=20, headers={"User-Agent": "UltraCLI/1.0"})
	resp.raise_for_status()
	text = resp.text
	return text[:max_chars]


def tool_web_readable(url: str, max_chars: int = 120_000) -> str:
	html = tool_web_fetch(url, max_chars=max_chars)
	soup = BeautifulSoup(html, "html.parser")
	for tag in soup(["script", "style", "noscript"]):
		tag.extract()
	text = soup.get_text("\n")
	return re.sub(r"\n{3,}", "\n\n", text).strip()[:max_chars]


def tool_str_find(text: str, pattern: str) -> List[int]:
	return [m.start() for m in re.finditer(pattern, text, flags=re.MULTILINE)]


def tool_str_replace(text: str, pattern: str, repl: str) -> str:
	return re.sub(pattern, repl, text, flags=re.MULTILINE)


def tool_code_insert(path: str, needle: str, insert: str, after: bool = True) -> str:
	data = tool_fs_read(path)
	idx = data.find(needle)
	if idx < 0:
		return "ERROR: needle not found"
	pos = idx + len(needle) if after else idx
	new_data = data[:pos] + insert + data[pos:]
	tool_fs_write(path, new_data)
	return "OK"


def build_default_registry() -> ToolRegistry:
	reg = ToolRegistry()
	reg.register(Tool("fs_read", "Read a file", tool_fs_read))
	reg.register(Tool("fs_write", "Write a file", tool_fs_write))
	reg.register(Tool("fs_copy", "Copy a file", tool_fs_copy))
	reg.register(Tool("sh", "Run a shell command", tool_shell))
	reg.register(Tool("web_fetch", "Fetch raw HTML/text from URL", tool_web_fetch))
	reg.register(Tool("web_readable", "Fetch readable text from URL", tool_web_readable))
	reg.register(Tool("str_find", "Find regex matches in text", tool_str_find))
	reg.register(Tool("str_replace", "Regex replace in text", tool_str_replace))
	reg.register(Tool("code_insert", "Insert code relative to a needle", tool_code_insert))
	return reg