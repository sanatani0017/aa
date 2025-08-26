from __future__ import annotations
import os
from typing import Any, Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from ..tools.registry import ToolRegistry
from .planner import ReActPlanner

console = Console()

SYSTEM_PROMPT = (
	"You are Astra, an autonomous coding pair programmer in CLI. "
	"Think, plan, then act. Prefer using tools. Keep outputs concise."
)


def run_interactive_session() -> None:
	registry = ToolRegistry.global_registry()
	planner = ReActPlanner(registry)
	console.print(Panel("Interactive session started. Type 'exit' to quit.", title="Astra", border_style="cyan"))
	while True:
		user = Prompt.ask("[bold]You[/bold]")
		if user.strip().lower() in {"exit", ":q", "quit"}:
			break
		for chunk in planner.run_task(user, system=SYSTEM_PROMPT):
			if chunk:
				console.print(chunk)


def run_one_off_task(task: str, use_planner: bool = True) -> None:
	registry = ToolRegistry.global_registry()
	planner = ReActPlanner(registry)
	for chunk in planner.run_task(task, system=SYSTEM_PROMPT):
		if chunk:
			console.print(chunk)