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
from .agent.planner import ReActPlanner
from .tools.registry import ToolRegistry
from . import memory

app = typer.Typer(add_completion=False, help="Astra: autonomous AI coding pair programmer (Gemini 2.5 Flash Lite)")
console = Console()

@app.command()
def help():
	console.print(Panel.fit("Astra CLI - Gemini 2.5 Flash Lite only\nCommands: chat, run, plan, tools", title="Astra", border_style="cyan"))

@app.command()
def chat(session: str = typer.Option("default", help="Session id for memory")):
	"""Start an interactive REPL-like coding session (Claude Code-like)."""
	bootstrap_runtime()
	memory.log_event(session, "system", "chat_start", {})
	run_interactive_session()
	memory.log_event(session, "system", "chat_end", {})

@app.command()
def run(task: str = typer.Argument(..., help="One-off task description"), plan: bool = typer.Option(True, help="Use planner"), session: str = typer.Option("default", help="Session id for memory")):
	"""Run a one-off autonomous task."""
	bootstrap_runtime()
	memory.log_event(session, "user", task, {})
	run_one_off_task(task, use_planner=plan)

@app.command()
def tools():
	"""List available tools."""
	bootstrap_runtime()
	registry = ToolRegistry.global_registry()
	rows = [f"- [bold]{t.name}[/bold]: {t.description}" for t in registry.list_tools()]
	console.print(Panel(Markdown("\n".join(rows)), title="Tools", border_style="green"))

@app.command()
def plan(task: str = typer.Argument(..., help="Plan only, do not execute")):
	"""Return a plan without executing tools."""
	bootstrap_runtime()
	planner = ReActPlanner(ToolRegistry.global_registry())
	text = planner.plan_only(task)
	console.print(Panel(Markdown(text), title="Plan", border_style="yellow"))

if __name__ == "__main__":
	app()