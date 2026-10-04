"""Extract concrete commitments + deadlines from rambly text using a local LLM (Ollama).

Deliberately conservative: only pulls things that sound like an actual promise
("I'll send X by Friday"), not vague intentions ("I should really get to that").
"""
import json
import re

import ollama

MODEL = "gemma3"  # swap for whatever Ollama model fits your hardware / your friend's speech style

SYSTEM_PROMPT = """You extract concrete COMMITMENTS from a transcript of someone talking or texting.

A commitment is something the speaker promised to DO for someone else, optionally with a deadline.
Examples that ARE commitments:
- "I'll send you the deck by Friday" -> task: send the deck, deadline: Friday
- "I'll call the landlord tomorrow" -> task: call the landlord, deadline: tomorrow
- "yeah I got you, I'll handle the invoice" -> task: handle the invoice, deadline: none

Examples that are NOT commitments (do not include these):
- "I should really get to that" (vague intention, no real promise)
- "maybe I'll look at it" (hedged, not committed)
- general chit-chat, opinions, or past events

Return ONLY a JSON array (no prose, no markdown fences). Each item:
{"task": "<short imperative description>", "deadline": "<as stated, or null>", "source_quote": "<the exact phrase from the transcript>"}

If there are no real commitments, return an empty array: []
"""


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    return match.group(1) if match else text


def _repair_truncated_array(text: str) -> str:
    """Best-effort fix for local models that emit a stop token before closing
    the JSON array (seen with llama3.2: valid objects, missing trailing ']')."""
    text = text.rstrip()
    if not text.startswith("["):
        return text
    # Drop a dangling partial/trailing-comma tail, then close the array.
    text = text.rstrip(",")
    last_close = text.rfind("}")
    if last_close != -1:
        text = text[: last_close + 1]
    if not text.endswith("]"):
        text += "]"
    return text


def extract_commitments(transcript: str) -> list[dict]:
    """Run the transcript through a local LLM and return a list of commitment dicts."""
    if not transcript.strip():
        return []

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        options={"temperature": 0.1},
    )
    content = response["message"]["content"]
    content = _strip_code_fence(content)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        try:
            parsed = json.loads(_repair_truncated_array(content))
        except json.JSONDecodeError:
            # Local models occasionally wrap/garble JSON; fail soft rather than crash the CLI.
            print(f"[warn] could not parse model output as JSON, skipping. Raw output:\n{content}")
            return []

    if not isinstance(parsed, list):
        return []

    commitments = []
    for item in parsed:
        if isinstance(item, dict) and item.get("task"):
            commitments.append(
                {
                    "task": item.get("task", "").strip(),
                    "deadline": item.get("deadline") or None,
                    "source_quote": item.get("source_quote", "").strip(),
                }
            )
    return commitments
