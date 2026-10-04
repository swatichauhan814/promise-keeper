# Promise Keeper

Your friend talks fast and says "yeah I'll send that over" or "I'll get you the file by Friday" a dozen times a day - then forgets. This tool listens to their rambly voice notes or texts and pulls out every actual commitment they made, with deadlines, into one clean todo list.

Built for Hacktoberfest "Build for a Friend" (open-source AI at its core).

## Why local / open-source matters here

- **It's a surveillance-shaped tool.** Transcribing someone's voice notes and texts to extract "what you promised" is sensitive by nature - this only works if your friend trusts it never leaves their machine. A cloud API is a non-starter for this use case.
- **No internet required.** Works on a commute, in a basement office, wherever the rambling happens.
- **Free to run constantly.** This only has value if it runs on *every* voice note, all day, forever - an API-metered version would get expensive or get disabled to save money, defeating the point.
- **Swappable model = tunable to the person.** ADHD commitment-speech is idiosyncratic ("I got you" = a promise, "maybe I'll look at it" = not). You can swap Ollama models or adjust the prompt until it matches how *your specific friend* talks, without waiting on a vendor.

## How it works

```
inputs/*.txt or *.m4a/*.wav   (texts pasted in, or voice notes)
        │
        ▼  faster-whisper (local, for audio only)
        ▼  Ollama local LLM - extracts commitments
todos.json                     (structured: task, deadline, source quote, status)
        │
        ▼
todos.md                       (human-readable running todo list)
```

The extractor is deliberately conservative: it only pulls things that sound like an actual commitment ("I'll send X by Y"), not vague intentions ("I should really...").

## Setup

1. Install [Ollama](https://ollama.com) and pull a model:
   ```bash
   ollama pull llama3.2
   ```
2. Create a virtualenv and install deps:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

Ingest a text note (pasted texts, journal entry, etc.):

```bash
python main.py ingest inputs/texts.txt
```

Ingest a voice memo (auto-transcribed first):

```bash
python main.py ingest inputs/voice_note.m4a
```

Ingest raw text directly from the command line:

```bash
python main.py ingest --text "yeah I'll send you the deck by Friday, and I'll call the landlord tomorrow about the sink"
```

See the running list:

```bash
python main.py list
```

Mark something done:

```bash
python main.py done 3
```

Every `ingest` appends newly-found commitments to `todos.json` and regenerates `todos.md`.

## Models used (all open-weight, run 100% locally)

| Stage | Model | Notes |
|---|---|---|
| Transcription (audio only) | `faster-whisper` (small) | Only invoked for audio files |
| Commitment extraction | Ollama (`llama3.2` default) | Swap models/prompt per how your friend talks |

## Project structure

```
promise-keeper/
├── inputs/              # drop text/audio notes here (gitignored except samples)
├── transcribe.py        # audio -> text via faster-whisper
├── extract_commitments.py  # text -> structured commitments via local LLM
├── todo_store.py         # todos.json read/write + todos.md rendering
├── main.py               # CLI: ingest / list / done
├── todos.json             # structured data (gitignored, it's personal)
├── todos.md               # human-readable list (gitignored, it's personal)
└── requirements.txt
```
