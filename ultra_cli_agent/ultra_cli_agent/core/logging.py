from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel

console = Console(theme=Theme({
    "info": "cyan",
    "warn": "yellow",
    "error": "bold red",
    "action": "magenta",
}))

class Logger:
    def __init__(self) -> None:
        pass

    def info(self, msg: str) -> None:
        console.print(f"[info]» {msg}")

    def action(self, msg: str) -> None:
        console.print(Panel(msg, title="action", style="action"))

    def warn(self, msg: str) -> None:
        console.print(f"[warn]» {msg}")

    def error(self, msg: str) -> None:
        console.print(f"[error]» {msg}")

logger = Logger()
