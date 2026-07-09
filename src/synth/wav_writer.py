from dataclasses import dataclass
from pathlib import Path
import wave

import numpy as np

from synth.audio import AudioBuffer


@dataclass(frozen=True)
class WavWriteSettings:
    """Immutable WAV writer settings.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-010
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-003 Oscillator En Audio Rendering
    - User Story: US-010 WAV Export
    - Version: 0.1.0
    """

    sample_width_bytes: int = 2


class WavWriter:
    """Write stereo audio buffers to PCM WAV files.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-010
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-003 Oscillator En Audio Rendering
    - User Story: US-010 WAV Export
    - Version: 0.1.0
    """

    def __init__(self, settings: WavWriteSettings | None = None) -> None:
        self._settings = settings if settings is not None else WavWriteSettings()

    def write(self, path: Path, buffer: AudioBuffer) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        clipped = np.clip(buffer.samples, -1.0, 1.0)
        pcm = (clipped * 32767.0).astype("<i2")
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(2)
            wav_file.setsampwidth(self._settings.sample_width_bytes)
            wav_file.setframerate(buffer.sample_rate)
            wav_file.writeframes(pcm.tobytes())
