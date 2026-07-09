from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from synth.audio import OutputChannel
from synth.debug import DebugLevel
from synth.oscillators import Waveform


@dataclass(frozen=True)
class OscillatorConfig:
    waveform: Waveform
    note: str
    amplitude: float


@dataclass(frozen=True)
class MidiConfig:
    default_input_device: str | None


@dataclass(frozen=True)
class PatchConfig:
    sample_rate: int
    duration_seconds: float
    channel: OutputChannel
    debuglevel: DebugLevel
    oscillator: OscillatorConfig
    midi: MidiConfig


class PatchConfigLoader:
    def load(self, path: Path) -> PatchConfig:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("Patch YAML must contain a mapping")
        return self.from_mapping(raw)

    def from_mapping(self, raw: dict[str, Any]) -> PatchConfig:
        oscillator_raw = raw.get("oscillator", {})
        if not isinstance(oscillator_raw, dict):
            raise ValueError("oscillator must be a mapping")
        midi_raw = raw.get("midi", {})
        if not isinstance(midi_raw, dict):
            raise ValueError("midi must be a mapping")

        return PatchConfig(
            sample_rate=int(raw.get("sample_rate", 44100)),
            duration_seconds=float(raw.get("duration_seconds", 1.0)),
            channel=OutputChannel(str(raw.get("channel", OutputChannel.STEREO.value))),
            debuglevel=DebugLevel(str(raw.get("debuglevel", DebugLevel.NONE.value))),
            oscillator=OscillatorConfig(
                waveform=Waveform(str(oscillator_raw.get("waveform", Waveform.SINE.value))),
                note=str(oscillator_raw.get("note", "C3")),
                amplitude=float(oscillator_raw.get("amplitude", 0.2)),
            ),
            midi=MidiConfig(default_input_device=midi_raw.get("default_input_device")),
        )

