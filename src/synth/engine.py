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

    def render_note(self, event: NoteEvent) -> AudioBuffer:
        mono = self._oscillator.generate(event.note.frequency_hz, event.duration_seconds) * event.velocity
        stereo = self._channel_router.route(mono.astype(np.float32), self._settings.channel)
        return AudioBuffer(samples=stereo, sample_rate=self._settings.sample_rate)

    def render_sequence(self, sequence: NoteSequence) -> AudioBuffer:
        total_samples = int(round(sequence.total_duration_seconds() * self._settings.sample_rate))
        if total_samples == 0:
            return AudioBuffer(samples=np.zeros((0, 2), dtype=np.float32), sample_rate=self._settings.sample_rate)

        mix = np.zeros(total_samples, dtype=np.float32)
        for event in sequence.events:
            rendered = self._oscillator.generate(event.note.frequency_hz, event.duration_seconds) * event.velocity
            start = int(round(event.start_seconds * self._settings.sample_rate))
            end = min(start + rendered.shape[0], total_samples)
            mix[start:end] += rendered[: end - start]

        mix = np.clip(mix, -1.0, 1.0).astype(np.float32)
        stereo = self._channel_router.route(mix, self._settings.channel)
        return AudioBuffer(samples=stereo, sample_rate=self._settings.sample_rate)

