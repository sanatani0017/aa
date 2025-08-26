from rich.console import Console
from rich.markdown import Markdown
import os

console = Console()

DEFAULT_SYSTEM_PROMPT = (
    "You are an autonomous coding pair programmer for CLI only. Use only Gemini 2.5 Flash Lite."
)

class Settings:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        self.system_prompt = os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)

settings = Settings()
