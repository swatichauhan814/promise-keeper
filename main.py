"""CLI: ingest voice notes/texts, extract commitments, maintain a todo list. 100% local."""
from pathlib import Path

import click

import todo_store
from extract_commitments import extract_commitments
from transcribe import is_audio_file, transcribe_audio


@click.group()
def cli():
    """Promise Keeper — turn rambly voice notes/texts into a real todo list, fully offline."""


@cli.command()
@click.argument("path", required=False, type=click.Path(exists=True, path_type=Path))
@click.option("--text", "raw_text", default=None, help="Pass raw text directly instead of a file.")
def ingest(path: Path | None, raw_text: str | None):
    """Ingest a text file, audio file, or --text string and extract commitments."""
    if raw_text:
        transcript = raw_text
        source = "cli-text"
    elif path:
        if is_audio_file(path):
            click.echo(f"Transcribing {path} (local Whisper)...")
            transcript = transcribe_audio(path)
        else:
            transcript = path.read_text(encoding="utf-8")
        source = str(path)
    else:
        raise click.UsageError("Provide a PATH or --text.")

    click.echo("Extracting commitments (local LLM)...")
    commitments = extract_commitments(transcript)

    if not commitments:
        click.echo("No commitments found.")
        return

    added = todo_store.add_commitments(commitments, source=source)
    click.echo(f"Added {len(added)} new commitment(s):")
    for c in added:
        deadline = f" (due {c['deadline']})" if c["deadline"] else ""
        click.echo(f"  #{c['id']} {c['task']}{deadline}")


@cli.command(name="list")
def list_todos():
    """Show pending and completed commitments."""
    todos = todo_store.load_todos()
    pending = [t for t in todos if t["status"] == "pending"]
    done = [t for t in todos if t["status"] == "done"]

    click.echo("Pending:")
    if not pending:
        click.echo("  (nothing pending)")
    for t in pending:
        deadline = f" (due {t['deadline']})" if t.get("deadline") else ""
        click.echo(f"  #{t['id']} {t['task']}{deadline}")

    click.echo("\nDone:")
    if not done:
        click.echo("  (nothing yet)")
    for t in done:
        click.echo(f"  #{t['id']} {t['task']}")


@cli.command()
@click.argument("todo_id", type=int)
def done(todo_id: int):
    """Mark a commitment as done by its #id."""
    if todo_store.mark_done(todo_id):
        click.echo(f"Marked #{todo_id} done.")
    else:
        click.echo(f"No commitment with id #{todo_id}.")


if __name__ == "__main__":
    cli()
