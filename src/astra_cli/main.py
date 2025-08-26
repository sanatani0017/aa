import os
import sys
import json
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from .runtime import bootstrap_runtime
from .agent.controller import run_interactive_session, run_one_off_task

app = typer.Typer(add_completion=False, help="Astra: autonomous AI coding pair programmer (Gemini 2.5 Flash Lite)")
console = Console()

@app.command()
def help():
	console.print(Panel.fit("Astra CLI - Gemini 2.5 Flash Lite only\nCommands: chat, run, plan, tools", title="Astra", border_style="cyan"))

@app.command()
def chat():
	"""Start an interactive REPL-like coding session (Claude Code-like)."""
	bootstrap_runtime()
	run_interactive_session()

@app.command()
def run(task: str = typer.Argument(..., help="One-off task description"), plan: bool = typer.Option(True, help="Use planner")):
	"""Run a one-off autonomous task."""
	bootstrap_runtime()
	run_one_off_task(task, use_planner=plan)

@app.command()
def tools():
	"""List available tools."""
	from .tools.registry import ToolRegistry
	bootstrap_runtime()
	registry = ToolRegistry.global_registry()
	rows = [f"- [bold]{t.name}[/bold]: {t.description}" for t in registry.list_tools()]
	console.print(Panel(Markdown("\n".join(rows)), title="Tools", border_style="green"))

if __name__ == "__main__":
	app()