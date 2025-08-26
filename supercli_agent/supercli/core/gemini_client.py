from __future__ import annotations
import os
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import httpx
from .config import Settings


GEMINI_API_URL = os.getenv(
    "GEMINI_API_URL",
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
)


@dataclass
class GeminiClient:
    settings: Settings
    _client: Optional[httpx.AsyncClient] = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60)
        return self._client

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        *,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 2048,
    ) -> str:
        client = await self._ensure_client()
        url = GEMINI_API_URL.format(model=self.settings.gemini_model)
        headers = {"Content-Type": "application/json"}
        params = {"key": self.settings.gemini_api_key}
        contents: List[Dict[str, Any]] = []
        if system:
            contents.append({"role": "user", "parts": [{"text": f"<system>{system}</system>"}]})
        for m in messages:
            role = m.get("role", "user")
            text = m.get("content", "")
            contents.append({"role": role, "parts": [{"text": text}]})
        body = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
            },
        }
        resp = await client.post(url, headers=headers, params=params, json=body)
        resp.raise_for_status()
        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return json.dumps(data)

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None