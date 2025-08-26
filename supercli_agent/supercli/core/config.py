from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class Settings:
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash-lite"

    @staticmethod
    def load() -> "Settings":
        key = os.getenv("GEMINI_API_KEY", "")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        return Settings(gemini_api_key=key, gemini_model=model)
