import json
import os
from typing import List, Dict, Any, Optional

import httpx

from ..core.logging import logger
from ..core.config import settings

GEMINI_API_ROOT = os.getenv(
	"GEMINI_API_ROOT",
	"https://generativelanguage.googleapis.com/v1beta",
)


class GeminiProvider:
	"""
	Thin wrapper around Gemini 2.5 Flash Lite generateContent API.
	Respects env:
	- GEMINI_API_KEY: API key
	- GEMINI_MODEL: default model name (default: gemini-2.5-flash-lite)
	- GEMINI_MOCK: if "1", returns mocked responses for offline/dev
	"""

	def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
		self.api_key = api_key or settings.gemini_api_key
		self.model = model or settings.model
		self.mock = os.getenv("GEMINI_MOCK", "0") == "1"

	def _endpoint(self) -> str:
		return f"{GEMINI_API_ROOT}/models/{self.model}:generateContent"

	def generate(
		self,
		messages: List[Dict[str, Any]],
		system_prompt: Optional[str] = None,
		json_response: bool = False,
		max_output_tokens: int = 2048,
	) -> str:
		"""
		messages: list of {role: "user"|"assistant"|"system", content: str}
		"""
		if self.mock:
			# Simple mock behavior for offline dev
			last_user = next((m for m in reversed(messages) if m.get("role") == "user"), None)
			content = last_user.get("content") if last_user else ""
			return json.dumps({
				"thought": "Mocked thinking.",
				"final": f"Echo: {content[:80]}"
			}) if json_response else f"Echo: {content}"

		api_key = self.api_key
		if not api_key:
			raise RuntimeError("GEMINI_API_KEY not set and GEMINI_MOCK!=1")

		headers = {
			"Content-Type": "application/json",
		}
		params = {"key": api_key}

		# Gemini expects contents array with parts; map chat messages accordingly
		contents: List[Dict[str, Any]] = []
		if system_prompt:
			contents.append({
				"role": "system",
				"parts": [{"text": system_prompt}],
			})
		for m in messages:
			role = m.get("role", "user")
			text = m.get("content", "")
			contents.append({"role": role, "parts": [{"text": text}]})

		req: Dict[str, Any] = {
			"contents": contents,
			"generationConfig": {
				"maxOutputTokens": max_output_tokens,
				"temperature": 0.2,
				"responseMimeType": "application/json" if json_response else "text/plain",
			},
		}

		with httpx.Client(timeout=60) as client:
			resp = client.post(self._endpoint(), params=params, headers=headers, json=req)
			if resp.status_code >= 400:
				logger.error(f"Gemini error {resp.status_code}: {resp.text[:300]}")
				raise RuntimeError(f"Gemini API error: {resp.status_code}")
			data = resp.json()

			# Response format: candidates[0].content.parts[*].text
			candidates = data.get("candidates", [])
			if not candidates:
				return ""
			parts = candidates[0].get("content", {}).get("parts", [])
			texts = [p.get("text", "") for p in parts]
			return "\n".join([t for t in texts if t])