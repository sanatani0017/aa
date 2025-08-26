from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

@dataclass
class Tool:
	name: str
	description: str
	parameters: Dict[str, Any]
	func: Callable[..., Any]

class ToolRegistry:
	_instance: Optional["ToolRegistry"] = None

	def __init__(self) -> None:
		self._tools: Dict[str, Tool] = {}
		self._model_client = None

	@classmethod
	def global_registry(cls) -> "ToolRegistry":
		if not cls._instance:
			cls._instance = ToolRegistry()
		return cls._instance

	def bind_model_client(self, client: Any) -> None:
		self._model_client = client

	def register(self, tool: Tool) -> None:
		self._tools[tool.name] = tool

	def get(self, name: str) -> Tool:
		return self._tools[name]

	def list_tools(self) -> List[Tool]:
		return list(self._tools.values())

	def register_default_tools(self) -> None:
		from . import fs, shell, strings, web, coding, repo, crawler
		for t in (
			fs.default_tools()
			+ shell.default_tools()
			+ strings.default_tools()
			+ web.default_tools()
			+ coding.default_tools()
			+ repo.default_tools()
			+ crawler.default_tools()
		):
			self.register(t)