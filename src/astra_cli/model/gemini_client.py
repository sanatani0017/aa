from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import httpx

@dataclass
class GeminiConfig:
	api_key: Optional[str]
	endpoint: str
	model: str

def _headers(api_key: Optional[str]) -> Dict[str, str]:
	h = {"Content-Type": "application/json"}
	if api_key:
		h["x-goog-api-key"] = api_key
	return h

class GeminiClient:
	"""Minimal Gemini 2.5 Flash Lite-only client. No fallback to other LLMs."""
	def __init__(self, config: GeminiConfig) -> None:
		self.config = config

	def generate(self, messages: List[Dict[str, Any]], tools_schema: Optional[Dict[str, Any]] = None, temperature: float = 0.2, system: Optional[str] = None) -> Dict[str, Any]:
		url = f"{self.config.endpoint}/v1beta/{self.config.model}:generateContent"
		payload: Dict[str, Any] = {
			"contents": self._convert_messages(messages),
			"generationConfig": {"temperature": temperature},
		}
		if system:
			payload["systemInstruction"] = {"role": "system", "parts": [{"text": system}]}
		if tools_schema:
			payload["tools"] = tools_schema.get("tools", [])
			payload["toolConfig"] = tools_schema.get("toolConfig", {"functionCallingConfig": {"mode": "AUTO"}})
		resp = httpx.post(url, headers=_headers(self.config.api_key), json=payload, timeout=60)
		resp.raise_for_status()
		return resp.json()

	def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		contents: List[Dict[str, Any]] = []
		for m in messages:
			role = "user" if m.get("role") == "user" else "model"
			parts: List[Dict[str, Any]] = []
			if "content" in m and m["content"]:
				parts.append({"text": m["content"]})
			if "tool_calls" in m:
				# Gemini expects function calls in tools; here we pass-through in higher layer
				pass
			contents.append({"role": role, "parts": parts})
		return contents