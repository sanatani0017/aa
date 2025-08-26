from __future__ import annotations
import json
import os
import time
from typing import Any, Dict, Iterable, List, Optional

DEFAULT_DIR = os.getenv("ASTRA_MEMORY_DIR", os.path.expanduser("~/.astra"))
SESS_FILE = os.path.join(DEFAULT_DIR, "sessions.jsonl")


def ensure_dirs() -> None:
	os.makedirs(DEFAULT_DIR, exist_ok=True)


def log_event(session_id: str, role: str, content: str, meta: Optional[Dict[str, Any]] = None) -> None:
	ensure_dirs()
	rec = {
		"ts": time.time(),
		"session": session_id,
		"role": role,
		"content": content,
		"meta": meta or {},
	}
	with open(SESS_FILE, "a", encoding="utf-8") as f:
		f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_session(session_id: str, limit: int = 200) -> List[Dict[str, Any]]:
	if not os.path.exists(SESS_FILE):
		return []
	rows: List[Dict[str, Any]] = []
	with open(SESS_FILE, "r", encoding="utf-8") as f:
		for line in f:
			try:
				obj = json.loads(line)
			except Exception:
				continue
			if obj.get("session") == session_id:
				rows.append(obj)
	return rows[-limit:]