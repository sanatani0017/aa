# Astra CLI Agent (Gemini 2.5 Flash Lite)

Terminal-only, autonomous AI coding pair programmer. ReAct-style planner, subagents, memory, repo-aware tools, web retrieval. Gemini 2.5 Flash Lite only.

Quick start:

```bash
export GEMINI_API_KEY=your_key
pip install -e .
~/.local/bin/astra help
```

Commands:

- `astra chat [--session default]`: Interactive REPL-like session
- `astra run "task description" [--plan/--no-plan] [--session default]`: One-off task
- `astra plan "task description"`: Plan only (no execution)
- `astra tools`: List available tools

Notes:
- No web UI. Terminal UX inspired by Claude Code.
- Memory stored at `~/.astra/sessions.jsonl`. Override with `ASTRA_MEMORY_DIR`.