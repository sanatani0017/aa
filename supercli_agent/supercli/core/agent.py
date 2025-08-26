from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .gemini_client import GeminiClient


SYSTEM_PROMPT = (
    "You are SuperCLI, an autonomous ReAct coding pair programmer. "
    "Think step-by-step, plan, then act using tools when necessary. "
    "Keep outputs concise for terminal."
)


@dataclass
class Memory:
    messages: List[Dict[str, Any]] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})


@dataclass
class Agent:
    client: GeminiClient
    memory: Memory = field(default_factory=Memory)

    async def chat(self, user_input: str) -> str:
        self.memory.add("user", user_input)
        reply = await self.client.generate(self.memory.messages, system=SYSTEM_PROMPT)
        self.memory.add("model", reply)
        return reply