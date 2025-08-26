import json
from typing import Any, Dict, List, Optional

from .logging import logger
from .tools import ToolRegistry, build_default_registry
from ..providers.gemini import GeminiProvider
from ..core.config import settings

THOUGHT_INSTRUCTIONS = (
	"""
	You are an autonomous CLI coding agent. Use Think-Plan-Do. When tools are needed,
	respond with a JSON block ONLY, with keys: {"tool": str, "args": object}.
	Otherwise, respond with a final natural language answer.
	Tools available will be listed. Keep steps small and iterate.
	"""
)


class PlannerExecutor:
	def __init__(self, tools: Optional[ToolRegistry] = None, model: Optional[GeminiProvider] = None) -> None:
		self.tools = tools or build_default_registry()
		self.model = model or GeminiProvider()

	def step(self, goal: str, history: List[Dict[str, str]]) -> str:
		messages: List[Dict[str, Any]] = []
		messages.append({"role": "system", "content": settings.system_prompt})
		messages.append({"role": "system", "content": THOUGHT_INSTRUCTIONS + "\nTools: " + ", ".join(self.tools.list())})
		for m in history:
			messages.append(m)
		messages.append({"role": "user", "content": goal})

		resp = self.model.generate(messages, json_response=False)
		return resp

	def run(self, goal: str, max_iters: int = 8) -> str:
		history: List[Dict[str, str]] = []
		for i in range(max_iters):
			logger.info(f"Plan iteration {i+1}")
			out = self.step(goal, history)
			text = out.strip()
			# Try parse as JSON tool call
			call = None
			if text.startswith("{"):
				try:
					call = json.loads(text)
				except Exception:
					call = None

			if call and isinstance(call, dict) and "tool" in call:
				tool_name = call.get("tool")
				args = call.get("args", {})
				logger.action(f"TOOL {tool_name} ← {args}")
				try:
					tool = self.tools.get(tool_name)
					result = tool.call(**args) if isinstance(args, dict) else tool.call(args)
					result_text = str(result)
				except Exception as e:
					result_text = f"ERROR: {e}"
				# Feed back result for next iteration
				history.append({"role": "assistant", "content": text})
				history.append({"role": "user", "content": f"TOOL_RESULT:\n{result_text[:8000]}"})
				continue

			# Treat as final answer
			return text

		return "Reached max iterations without final answer."