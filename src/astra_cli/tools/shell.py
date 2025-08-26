from __future__ import annotations
import subprocess
from typing import List
from .registry import Tool


def _run(cmd: str, timeout: int = 120) -> str:
	completed = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
	return completed.stdout.decode("utf-8", errors="ignore")


def default_tools() -> List[Tool]:
	return [
		Tool(name="sh", description="Run a shell command (stdout+stderr)", parameters={"cmd": str, "timeout": int}, func=lambda cmd, timeout=120: _run(cmd, timeout)),
	]