from __future__ import annotations
import json
from typing import Any, Dict, Generator, List, Optional
from ..tools.registry import ToolRegistry, Tool
from ..model.gemini_client import GeminiClient

THINK_PROMPT = (
	"Follow ReAct. Use tools via function calls when helpful. "
	"When planning complex work, decompose into subtasks."
)

class ReActPlanner:
	def __init__(self, registry: ToolRegistry) -> None:
		self.registry = registry
		self.client: GeminiClient = registry._model_client  # type: ignore

	def _tool_schema(self) -> Dict[str, Any]:
		tools_json = []
		for t in self.registry.list_tools():
			params = {name: {"type": _pytype_to_jsonschema(tp)} for name, tp in t.parameters.items()}
			tools_json.append({
				"functionDeclarations": [{
					"name": t.name,
					"description": t.description,
					"parameters": {"type": "object", "properties": params}
				}]
			})
		return {"tools": tools_json}

	def run_task(self, task: str, system: Optional[str] = None) -> Generator[str, None, None]:
		messages: List[Dict[str, Any]] = [{"role": "user", "content": f"Task: {task}\n\n{THINK_PROMPT}"}]
		for _ in range(6):  # bounded ReAct steps
			resp = self.client.generate(messages, tools_schema=self._tool_schema(), system=system)
			text, fcalls = _parse_gemini_response(resp)
			if text:
				yield text
			if not fcalls:
				break
			obs_text = []
			for call in fcalls:
				name = call.get("name")
				args = call.get("args", {})
				tool = self.registry.get(name)
				result = tool.func(**args)
				obs_text.append(f"{name} -> {str(result)[:2000]}")
			messages.append({"role": "user", "content": "\n".join([f"Observation: {o}" for o in obs_text])})

	def plan_only(self, task: str, system: Optional[str] = None) -> str:
		prompt = (
			"You are planning only. Provide: Goals, Risks, Steps, Tools to use, and Stop. "
			"Do NOT execute tools."
		)
		resp = self.client.generate([{"role": "user", "content": f"Task: {task}\n\n{prompt}"}], tools_schema=None, system=system)
		text, _ = _parse_gemini_response(resp)
		return text


def _parse_gemini_response(resp: Dict[str, Any]) -> tuple[str, List[Dict[str, Any]]]:
	text_out = ""
	function_calls: List[Dict[str, Any]] = []
	cands = resp.get("candidates", [])
	if not cands:
		return text_out, function_calls
	parts = cands[0].get("content", {}).get("parts", [])
	for p in parts:
		if "text" in p:
			text_out += p.get("text", "")
		if "functionCall" in p:
			fc = p["functionCall"]
			function_calls.append({"name": fc.get("name"), "args": fc.get("args", {})})
	return text_out.strip(), function_calls


def _pytype_to_jsonschema(tp: Any) -> str:
	return "string" if tp is str else ("integer" if tp is int else ("boolean" if tp is bool else "string"))