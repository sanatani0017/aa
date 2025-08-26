from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class SubTask:
	description: str
	callable: Callable[[], Any]


def execute_subtasks_parallel(subtasks: List[SubTask], max_workers: int = 4) -> List[Any]:
	results: List[Any] = []
	with ThreadPoolExecutor(max_workers=max_workers) as ex:
		futs = {ex.submit(t.callable): t for t in subtasks}
		for fut in as_completed(futs):
			results.append(fut.result())
	return results