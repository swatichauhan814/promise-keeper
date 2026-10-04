"""Transcribe audio files to text using faster-whisper (local, open-weight, offline)."""
from pathlib import Path

from faster_whisper import WhisperModel

MODEL_SIZE = "small"  # tiny/base = faster, small/medium = better for fast/rambly speech

_model: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


def transcribe_audio(audio_path: Path) -> str:
    """Transcribe a single audio file and return the full text."""
    model = _get_model()
    segments, _info = model.transcribe(str(audio_path), beam_size=5)
    return " ".join(segment.text.strip() for segment in segments)


AUDIO_EXTENSIONS = {".m4a", ".wav", ".mp3", ".mp4", ".ogg", ".flac"}


def is_audio_file(path: Path) -> bool:
    return path.suffix.lower() in AUDIO_EXTENSIONS
