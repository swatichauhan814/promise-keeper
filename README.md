# Promise Keeper

Promise Keeper is an ADHD-friendly tool for getting commitments out of your head and into a clear, manageable list. It turns text or voice notes like "yeah, I'll send that over" or "I'll get you the file by Friday" into todos with deadlines, so you don't have to rely on remembering every promise later.

Remembering, organizing, and following up on commitments can be difficult for people with ADHD, especially when plans are made in passing. Promise Keeper offers a lightweight external memory: capture what was said, review the extracted commitments, and mark them done when you're ready. ADHD experiences vary, and this is a practical support tool—not a treatment or a substitute for professional care.

Built for Hacktoberfest "Build for a Friend" with open-source AI at its core.

## Designed for ADHD-friendly follow-through

- **Capture without relying on memory.** Turn a voice memo, pasted message, or quick note into a list you can come back to.
- **Make next steps visible.** Keep the task, deadline, and original quote together, then mark commitments done as you complete them.
- **Keep control of personal information.** Notes and commitments can contain sensitive details, so processing stays on your machine rather than being sent to a cloud AI service.
- **No internet required.** Works on a commute, in a basement office, wherever the rambling happens.
- **Adaptable to your communication style.** Commitment language is personal. You can swap Ollama models or adjust the extraction prompt to better match how you phrase plans and promises.
- **No per-note AI fee.** Once installed, local processing doesn't charge per voice note or text.

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

The extractor is deliberately conservative: it looks for clear commitments ("I'll send X by Y"), not vague intentions ("I should really..."). Review the results before relying on them; automated extraction can miss context or misunderstand what you meant.

## Limitations

Promise Keeper helps with *capturing and organizing* commitments, but it isn't a complete ADHD solution on its own:

- **Capture is manual, not automatic.** You still have to copy/paste text (e.g. from WhatsApp, iMessage, email) into a file or `--text` flag, or save a voice note, and run `ingest` yourself. There's no inbox watcher, clipboard monitor, or messaging-app integration — if initiating that step is the hard part some days, this tool won't remove that barrier.
- **No reminders or notifications.** Deadlines are stored as plain text (e.g. "Friday"), not calendar events or alarms. You have to remember to run `python main.py list` or open `todos.md` to see what's due — nothing pushes a nudge to you.
- **CLI-only.** There's no GUI, menu bar app, or mobile client (aside from the browser-only `demo/`, which doesn't use the real AI pipeline or persist data).
- **No calendar sync.** Deadlines aren't converted into actual date/time objects or synced to any calendar.

In short: it's a lightweight capture-and-review layer for people who already have (or are building) the habit of pasting notes somewhere. Pair it with an external reminder/notification system for the time-based nudging ADHD workflows often need.

## Setup

1. Install [Ollama](https://ollama.com) and pull a model:
   ```bash
   ollama pull gemma3
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

## Public demo

The `demo/` directory contains an interactive, browser-only text preview. Visitors can
edit sample transcripts or paste their own text, find likely promises and deadlines,
and mark them done for the current tab session. The demo uses simple rules, not the
Ollama model: it may miss nuanced commitments, and it does not transcribe audio.
Text is not uploaded or saved; refreshing resets the page. The full AI-powered CLI
continues to run locally.

Render serves `demo/` as a static site using the included `render.yaml`; the
interaction runs entirely in visitors' browsers. Push changes to `main` to update
the existing Render demo (when automatic deploys are enabled). To create a new
deployment, create a Blueprint from this repository using `render.yaml`.

## Models used (all open-weight, run 100% locally)

| Stage | Model | Notes |
|---|---|---|
| Transcription (audio only) | `faster-whisper` (small) | Only invoked for audio files |
| Commitment extraction | Ollama (`gemma3` default) | Swap models/prompt per how your friend talks |

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
