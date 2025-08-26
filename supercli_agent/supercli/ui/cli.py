from __future__ import annotations
import os
import asyncio
import click
from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

from supercli.core.config import Settings
from supercli.core.gemini_client import GeminiClient
from supercli.core.agent import Agent

console = Console()

async def run_cli() -> None:
    console.print("[bold cyan]supercli-agent[/] - Gemini 2.5 Flash Lite only. No web UI.")
    session = PromptSession()
    completer = WordCompleter(["chat", "tools", "exit"], ignore_case=True)
    settings: Settings
    try:
        settings = Settings.load()
    except Exception as e:
        console.print(f"[red]Config error:[/] {e}")
        console.print("Set GEMINI_API_KEY and try again.")
        return
    client = GeminiClient(settings=settings)
    agent = Agent(client=client)
    try:
        while True:
            try:
                cmd = await asyncio.to_thread(session.prompt, "> ", completer=completer)
            except (KeyboardInterrupt, EOFError):
                console.print("\nGoodbye.")
                break
            cmd = cmd.strip()
            if cmd in ("exit", "quit"):
                break
            if cmd == "tools":
                console.print("Tools will be listed here.")
                continue
            if cmd.startswith("chat"):
                prompt = cmd[len("chat"):].strip()
                if not prompt:
                    prompt = await asyncio.to_thread(session.prompt, "message: ")
                console.print("[dim]Thinking...[/]")
                try:
                    reply = await agent.chat(prompt)
                except Exception as e:
                    console.print(f"[red]Error:[/] {e}")
                    continue
                console.print(reply)
                continue
            console.print(f"Unknown command: {cmd}")
    finally:
        await client.aclose()
