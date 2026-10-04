"""Persistence for extracted commitments: todos.json (data) + todos.md (human-readable)."""
import json
from datetime import datetime
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent
TODOS_JSON = _BASE_DIR / "todos.json"
TODOS_MD = _BASE_DIR / "todos.md"


def load_todos() -> list[dict]:
    if not TODOS_JSON.exists():
        return []
    return json.loads(TODOS_JSON.read_text(encoding="utf-8"))


def save_todos(todos: list[dict]) -> None:
    TODOS_JSON.write_text(json.dumps(todos, indent=2), encoding="utf-8")
    _render_markdown(todos)


def add_commitments(new_commitments: list[dict], source: str) -> list[dict]:
    """Append new commitments (with dedupe on task+deadline) and persist. Returns the added ones."""
    todos = load_todos()
    existing_keys = {(t["task"].lower(), t.get("deadline")) for t in todos}

    added = []
    next_id = max((t["id"] for t in todos), default=0) + 1
    for c in new_commitments:
        key = (c["task"].lower(), c.get("deadline"))
        if key in existing_keys:
            continue
        entry = {
            "id": next_id,
            "task": c["task"],
            "deadline": c.get("deadline"),
            "source_quote": c.get("source_quote", ""),
            "source": source,
            "status": "pending",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        todos.append(entry)
        added.append(entry)
        existing_keys.add(key)
        next_id += 1

    if added:
        save_todos(todos)
    return added


def mark_done(todo_id: int) -> bool:
    todos = load_todos()
    for t in todos:
        if t["id"] == todo_id:
            t["status"] = "done"
            t["completed_at"] = datetime.now().isoformat(timespec="seconds")
            save_todos(todos)
            return True
    return False


def _render_markdown(todos: list[dict]) -> None:
    pending = [t for t in todos if t["status"] == "pending"]
    done = [t for t in todos if t["status"] == "done"]

    lines = ["# Promises to Keep\n"]

    lines.append("## Pending\n")
    if not pending:
        lines.append("_Nothing pending - nice._\n")
    for t in pending:
        deadline = f" - **due {t['deadline']}**" if t.get("deadline") else ""
        lines.append(f"- [ ] (#{t['id']}) {t['task']}{deadline}")
        if t.get("source_quote"):
            lines.append(f'  > "{t["source_quote"]}"')
    lines.append("")

    lines.append("## Done\n")
    if not done:
        lines.append("_Nothing completed yet._\n")
    for t in done:
        lines.append(f"- [x] (#{t['id']}) {t['task']}")

    TODOS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
