# Bestand: engine.py
# Versienummer: 0.1.0
# Doel: Synth audio rendering en polyphonic voice mixing.
# Sprint: Future MIDI/DAW
# User-Story: US-034 Polyphonic Voice Mixer En Triads
# Actie: US-034-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-034

from dataclasses import dataclass

import numpy as np

from synth.audio import AudioBuffer, ChannelRouter, OutputChannel
from synth.notes import NoteEvent, NoteSequence
from synth.oscillators import Oscillator, OscillatorSettings, Waveform


@dataclass(frozen=True)
class SynthEngineSettings:
    sample_rate: int
    waveform: Waveform
    amplitude: float
    channel: OutputChannel


class PolyphonicVoiceMixer:
    """Mix overlapping NoteEvent voices into a single mono buffer.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-034
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-034 Polyphonic Voice Mixer En Triads
    - Version: 0.1.0
    """

    def __init__(self, oscillator: Oscillator) -> None:
        self._oscillator = oscillator

    def mix(self, events: tuple[NoteEvent, ...], total_samples: int, sample_rate: int) -> np.ndarray:
        mix = np.zeros(total_samples, dtype=np.float32)
        for event in events:
            rendered = self._oscillator.generate(event.note.frequency_hz, event.duration_seconds) * event.velocity
            start = int(round(event.start_seconds * sample_rate))
            end = min(start + rendered.shape[0], total_samples)
            if end <= start:
                continue
            mix[start:end] += rendered[: end - start]
        return np.clip(mix, -1.0, 1.0).astype(np.float32)


class SynthEngine:
    def __init__(self, settings: SynthEngineSettings) -> None:
        self._settings = settings
        self._oscillator = Oscillator(
            OscillatorSettings(
                waveform=settings.waveform,
                sample_rate=settings.sample_rate,
                amplitude=settings.amplitude,
            )
        )
        self._channel_router = ChannelRouter()
        self._polyphonic_mixer = PolyphonicVoiceMixer(self._oscillator)

    def render_note(self, event: NoteEvent) -> AudioBuffer:
        mono = self._oscillator.generate(event.note.frequency_hz, event.duration_seconds) * event.velocity
        stereo = self._channel_router.route(mono.astype(np.float32), self._settings.channel)
        return AudioBuffer(samples=stereo, sample_rate=self._settings.sample_rate)

    def render_sequence(self, sequence: NoteSequence) -> AudioBuffer:
        total_samples = int(round(sequence.total_duration_seconds() * self._settings.sample_rate))
        if total_samples == 0:
            return AudioBuffer(samples=np.zeros((0, 2), dtype=np.float32), sample_rate=self._settings.sample_rate)

        mix = self._polyphonic_mixer.mix(sequence.events, total_samples, self._settings.sample_rate)
        stereo = self._channel_router.route(mix, self._settings.channel)
        return AudioBuffer(samples=stereo, sample_rate=self._settings.sample_rate)
