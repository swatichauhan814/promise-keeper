*This is a submission for the [Hacktoberfest Weekend Challenge: Build for a Friend](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01)*

## What I Built

**Promise Keeper** - a CLI that listens to a friend's rambly voice notes or texts and pulls out every actual commitment they made, with deadlines, into one clean todo list.

I built this for a friend who talks fast and says things like "yeah I'll send that over" or "I'll get you the file by Friday" a dozen times a day - and then forgets half of them. She doesn't need a project management app, she needs something that listens to how she already talks (voice memos, rambly texts) and quietly extracts the promises buried in it, without ever judging the chit-chat around them.

It's deliberately conservative: "I'll send you the deck by Friday" counts as a commitment. "I should really get to that" or "maybe I'll look at it" doesn't. The goal isn't a transcript - it's a short list of things she actually said she'd do.

```
inputs/*.txt or *.m4a/*.wav   (texts pasted in, or voice notes)
        │
        ▼  faster-whisper (local, for audio only)
        ▼  local LLM via Ollama - extracts commitments
todos.json                     (structured: task, deadline, source quote, status)
        │
        ▼
todos.md                       (human-readable running todo list)
```

## Demo

No hosted demo - this runs entirely on-device, which is the point (more on that below). Here's a real run against `inputs/texts.txt`:

**Input (pasted texts):**
> hey sorry been slammed. yeah I'll send you the deck by friday for sure. oh and remind me, I told sam I'd call the landlord tomorrow about the sink. honestly I should probably clean my room too lol but anyway yeah I got you on the invoice thing, I'll have it handled by end of week

**Command:**
```bash
python main.py ingest inputs/texts.txt
```

**Output (`todos.md`):**
```markdown
# Promises to Keep

## Pending

- [ ] (#1) send the deck - **due Friday**
  > "yeah I'll send you the deck by Friday"
- [ ] (#3) handle the invoice - **due end of week**
  > "yeah I got you, I'll have it handled by end of week"

## Done

- [x] (#2) call the landlord
```

Note what *didn't* make the list: "I should probably clean my room" - a vague intention, correctly filtered out. That filtering is the whole product.

## Code

{% github swatichauhan814/promise-keeper %}

## How I Built It

Two local, open-weight models, chained together:

| Stage | Model | Notes |
|---|---|---|
| Transcription (audio only) | `faster-whisper` (small, int8, CPU) | Only invoked when the input is audio |
| Commitment extraction | Ollama running `gemma3` (4B) | Swappable - see below |

The pipeline is small on purpose: `transcribe.py` turns audio into text, `extract_commitments.py` sends that text to a local LLM with a tightly-scoped system prompt (examples of what *is* and *isn't* a commitment), and `todo_store.py` persists the structured results to `todos.json` and renders `todos.md`.

The one real engineering problem was that `llama3.2` at low temperature reliably produces valid JSON objects but sometimes cuts off before the closing `]` of the array - it emits a stop token early. Rather than fight the model with more prompt engineering, I just wrote `_repair_truncated_array()` to trim trailing commas, find the last complete `}`, and close the array myself. Small local models need this kind of defensive parsing a lot more than hosted frontier models do - which is a real cost of going local, and worth being honest about.

```python
def _repair_truncated_array(text: str) -> str:
    """Best-effort fix for local models that emit a stop token before closing
    the JSON array (seen with llama3.2: valid objects, missing trailing ']')."""
    text = text.rstrip()
    if not text.startswith("["):
        return text
    text = text.rstrip(",")
    last_close = text.rfind("}")
    if last_close != -1:
        text = text[: last_close + 1]
    if not text.endswith("]"):
        text += "]"
    return text
```

## Why Does Open Innovation Matter?

This is, structurally, a surveillance tool - it listens to a person's voice notes and texts and extracts "what you promised." That only works if the person trusts it never leaves their machine. A cloud API is a non-starter here, not because of cost, but because of consent: my friend would never record herself candidly into something that ships her rambling to a third-party server.

Open-weight models running on Ollama make three things possible that a closed API doesn't:

- **It never leaves the laptop.** No network call, no vendor, no data-retention policy to trust - just a model file on disk.
- **It can run on everything, forever.** This tool is only useful if it runs on *every* voice note, constantly. A per-token API bill is exactly the kind of thing that gets "optimized" into disablement the first time someone looks at a bill.
- **It's tunable to one specific person.** ADHD-adjacent commitment-speech is idiosyncratic - "I got you" is a promise, "maybe I'll look at it" isn't, and where that line sits differs friend to friend. Swapping the local model or hand-editing the extraction prompt until it matches *her* speech patterns is a five-minute edit to `extract_commitments.py`. With a closed API you're tuning a prompt against someone else's model and hoping the next version doesn't shift the behavior under you.

## Prize Categories

Best Use of Gemma

---

*Built for a friend who deserves to stop forgetting what she promised people - without a cloud service listening in to make that happen.*
