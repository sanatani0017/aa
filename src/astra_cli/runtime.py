import os
from typing import Optional
from .tools.registry import ToolRegistry
from .model.gemini_client import GeminiClient, GeminiConfig

_bootstrapped = False

def bootstrap_runtime() -> None:
	global _bootstrapped
	if _bootstrapped:
		return
	# Configure model (Gemini 2.5 Flash Lite only)
	api_key = os.getenv("GEMINI_API_KEY")
	endpoint = os.getenv("GEMINI_API_ENDPOINT", "https://generativelanguage.googleapis.com")
	model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash-lite-exp")
	client = GeminiClient(GeminiConfig(api_key=api_key, endpoint=endpoint, model=model_name))
	# Register tools
	registry = ToolRegistry.global_registry()
	registry.register_default_tools()
	registry.bind_model_client(client)
	_bootstrapped = True