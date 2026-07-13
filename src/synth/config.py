# Bestand: config.py
# Versienummer: 0.1.0
# Doel: YAML patch configuratie voor render, MIDI defaults en performance playback.
# Sprint: Future MIDI/DAW
# User-Story: US-042 MIDI Performance Patch YAML Config
# Actie: US-042-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-042

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from synth.audio import OutputChannel
from synth.debug import DebugLevel
from synth.oscillators import Waveform


@dataclass(frozen=True)
class OscillatorConfig:
    """Oscillator section loaded from a YAML patch.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-005 Configuratie En CLI
    - User Story: US-014 YAML Patch Config
    - User Story: US-042 MIDI Performance Patch YAML Config
    - Version: 0.1.0
    """

    waveform: Waveform
    note: str
    amplitude: float


@dataclass(frozen=True)
class MidiPerformanceConfig:
    """MIDI live-performance defaults loaded from a YAML patch.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-042 MIDI Performance Patch YAML Config
    - Version: 0.1.0
    """

    port_name: str | None = None
    max_messages: int | None = None
    timeout_seconds: float | None = None
    poll_interval_seconds: float | None = None
    note_duration_seconds: float | None = None
    voice_mode: str | None = None
    dedupe_window_seconds: float | None = None
    chord_window_seconds: float | None = None
    pitch_bend_range_semitones: float | None = None
    pitch_bend_channel_mode: str | None = None
    max_control_messages: int | None = None
    modulation_vibrato_depth_semitones: float | None = None
    modulation_vibrato_rate_hz: float | None = None
    run_until_interrupted: bool | None = None
    attack_time_seconds: float | None = None
    decay_time_seconds: float | None = None
    sustain_level: float | None = None
    release_time_seconds: float | None = None
    sample_rate: int | None = None
    waveform: str | None = None
    amplitude: float | None = None
    channel: str | None = None
    audio_device: str | None = None


@dataclass(frozen=True)
class MidiConfig:
    """MIDI section loaded from a YAML patch.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-005 Configuratie En CLI
    - User Story: US-025 MIDI Device Discovery En Default Selection
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-042 MIDI Performance Patch YAML Config
    - Version: 0.1.0
    """

    default_input_device: str | None
    performance: MidiPerformanceConfig


@dataclass(frozen=True)
class PatchConfig:
    """Complete YAML patch config for render and MIDI performance workflows.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-005 Configuratie En CLI
    - User Story: US-014 YAML Patch Config
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-042 MIDI Performance Patch YAML Config
    - Version: 0.1.0
    """

    sample_rate: int
    duration_seconds: float
    channel: OutputChannel
    debuglevel: DebugLevel
    oscillator: OscillatorConfig
    midi: MidiConfig


class PatchConfigLoader:
    """Loads YAML patch mappings into typed configuration objects.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-005 Configuratie En CLI
    - User Story: US-014 YAML Patch Config
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-042 MIDI Performance Patch YAML Config
    - Version: 0.1.0
    """

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
        performance_raw = midi_raw.get("performance", {})
        if performance_raw is None:
            performance_raw = {}
        if not isinstance(performance_raw, dict):
            raise ValueError("midi.performance must be a mapping")

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
            midi=MidiConfig(
                default_input_device=midi_raw.get("default_input_device"),
                performance=self._performance_from_mapping(performance_raw),
            ),
        )

    def _performance_from_mapping(self, raw: dict[str, Any]) -> MidiPerformanceConfig:
        return MidiPerformanceConfig(
            port_name=self._optional_str(raw, "port_name"),
            max_messages=self._optional_int(raw, "max_messages"),
            timeout_seconds=self._optional_float(raw, "timeout_seconds"),
            poll_interval_seconds=self._optional_float(raw, "poll_interval_seconds"),
            note_duration_seconds=self._optional_float(raw, "note_duration_seconds"),
            voice_mode=self._optional_str(raw, "voice_mode"),
            dedupe_window_seconds=self._optional_float(raw, "dedupe_window_seconds"),
            chord_window_seconds=self._optional_float(raw, "chord_window_seconds"),
            pitch_bend_range_semitones=self._optional_float(raw, "pitch_bend_range_semitones"),
            pitch_bend_channel_mode=self._optional_str(raw, "pitch_bend_channel_mode"),
            max_control_messages=self._optional_int(raw, "max_control_messages"),
            modulation_vibrato_depth_semitones=self._optional_float(raw, "modulation_vibrato_depth_semitones"),
            modulation_vibrato_rate_hz=self._optional_float(raw, "modulation_vibrato_rate_hz"),
            run_until_interrupted=self._optional_bool(raw, "run_until_interrupted"),
            attack_time_seconds=self._optional_float(raw, "attack_time_seconds"),
            decay_time_seconds=self._optional_float(raw, "decay_time_seconds"),
            sustain_level=self._optional_float(raw, "sustain_level"),
            release_time_seconds=self._optional_float(raw, "release_time_seconds"),
            sample_rate=self._optional_int(raw, "sample_rate"),
            waveform=self._optional_str(raw, "waveform"),
            amplitude=self._optional_float(raw, "amplitude"),
            channel=self._optional_str(raw, "channel"),
            audio_device=self._optional_str(raw, "audio_device"),
        )

    def _optional_str(self, raw: dict[str, Any], key: str) -> str | None:
        value = raw.get(key)
        if value is None:
            return None
        return str(value)

    def _optional_int(self, raw: dict[str, Any], key: str) -> int | None:
        value = raw.get(key)
        if value is None:
            return None
        return int(value)

    def _optional_float(self, raw: dict[str, Any], key: str) -> float | None:
        value = raw.get(key)
        if value is None:
            return None
        return float(value)

    def _optional_bool(self, raw: dict[str, Any], key: str) -> bool | None:
        value = raw.get(key)
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "yes", "1", "on"}:
                return True
            if normalized in {"false", "no", "0", "off"}:
                return False
        return bool(value)
