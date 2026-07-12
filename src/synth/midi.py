# Bestand: midi.py
# Versienummer: 0.1.0
# Doel: MIDI device discovery, device selectie, virtual MIDI audio trigger en MIDI-naar-NoteEvent mapping.
# Sprint: Future MIDI/DAW
# User-Story: US-041 Amp Envelope ADSR Parameters
# Actie: US-041-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-041

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
import json
import math
import platform
import subprocess
import sys
import time
from typing import Protocol

from synth.audio import (
    AudioBuffer,
    OutputChannel,
    SoundDeviceAudioPlayer,
    SoundDeviceSustainedAudioPlayer,
    SustainedAudioPlayerSettings,
)
from synth.engine import SynthEngine, SynthEngineSettings
from synth.notes import NoteEvent, NoteParser, NoteSequence
from synth.oscillators import Waveform


@dataclass(frozen=True)
class MidiDevice:
    identifier: str
    name: str
    direction: str


@dataclass(frozen=True)
class MidiDeviceSelection:
    """Selected MIDI input device request and optional resolved runtime device.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-025
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-025 MIDI Device Discovery En Default Selection
    - Version: 0.1.0
    """

    selected_device: str | None
    source: str
    matched_device: MidiDevice | None = None
    message: str = ""
    available_input_devices: tuple[MidiDevice, ...] = tuple()


@dataclass(frozen=True)
class MidiDeviceScanResult:
    """Result for safe MIDI device discovery diagnostics.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-022-BLOCKER
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-022 USB MIDI Hardware Input
    - Version: 0.1.0
    """

    devices: tuple[MidiDevice, ...]
    error_message: str | None
    backend_name: str = "mido/python-rtmidi"
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class MidiMessage:
    """Protocol-level MIDI message normalized for virtual input tests.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-020
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-020 Virtual MIDI Input Voor DAW
    - User Story: US-036 MIDI Pitch Bend Mapping En DSP
    - User Story: US-037 MIDI Modulation CC1 Mapping En DSP
    - Version: 0.1.0
    """

    message_type: str
    note_number: int
    velocity: int
    channel: int
    time_seconds: float = 0.0
    pitch_bend_value: int = 0
    control_number: int = 0
    control_value: int = 0

    def __post_init__(self) -> None:
        if self.message_type not in {"note_on", "note_off", "pitch_bend", "control_change"}:
            raise ValueError("message_type must be note_on, note_off, pitch_bend or control_change")
        if not 1 <= self.channel <= 16:
            raise ValueError("channel must be between 1 and 16")
        if self.time_seconds < 0:
            raise ValueError("time_seconds must not be negative")
        if self.message_type == "pitch_bend":
            if not -8192 <= self.pitch_bend_value <= 8191:
                raise ValueError("pitch_bend_value must be between -8192 and 8191")
            return
        if self.message_type == "control_change":
            if not 0 <= self.control_number <= 127:
                raise ValueError("control_number must be between 0 and 127")
            if not 0 <= self.control_value <= 127:
                raise ValueError("control_value must be between 0 and 127")
            return
        if not 0 <= self.note_number <= 127:
            raise ValueError("note_number must be between 0 and 127")
        if not 0 <= self.velocity <= 127:
            raise ValueError("velocity must be between 0 and 127")


@dataclass(frozen=True)
class VirtualMidiInputSettings:
    """Settings for future virtual MIDI input routes from a DAW.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-020
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-020 Virtual MIDI Input Voor DAW
    - Version: 0.1.0
    """

    input_name: str = "python-d1-synth"
    default_note_duration_seconds: float = 1.0

    def __post_init__(self) -> None:
        if not self.input_name.strip():
            raise ValueError("input_name must not be empty")
        if self.default_note_duration_seconds <= 0:
            raise ValueError("default_note_duration_seconds must be positive")


@dataclass(frozen=True)
class VirtualMidiInputDiagnostic:
    """Diagnostic result for a virtual MIDI input route.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-020
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-020 Virtual MIDI Input Voor DAW
    - Version: 0.1.0
    """

    available: bool
    message: str


@dataclass(frozen=True)
class UsbMidiInputDiagnostic:
    """Readiness result for generic USB MIDI input hardware.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-022
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-022 USB MIDI Hardware Input
    - Version: 0.1.0
    """

    ready: bool
    message: str
    selected_device: MidiDevice | None
    compatible_devices: tuple[MidiDevice, ...]


@dataclass(frozen=True)
class MidiInputReceiveSettings:
    """Settings for a bounded live MIDI input receive loop.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-026
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-026 Live MIDI Input Receive Loop
    - Version: 0.1.0
    """

    input_name: str
    max_messages: int = 10
    timeout_seconds: float = 5.0

    def __post_init__(self) -> None:
        if not self.input_name.strip():
            raise ValueError("input_name must not be empty")
        if self.max_messages <= 0:
            raise ValueError("max_messages must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


@dataclass(frozen=True)
class MidiInputReceiveResult:
    """Result from a bounded live MIDI input receive loop.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-026
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-026 Live MIDI Input Receive Loop
    - Version: 0.1.0
    """

    input_name: str
    received_messages: tuple[MidiMessage, ...]
    note_sequence: NoteSequence
    message: str


@dataclass(frozen=True)
class VirtualMidiPortSettings:
    """Settings for opening a bounded virtual MIDI input port.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-027
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-027 Virtual MIDI Port Voor Logic/DAW
    - Version: 0.1.0
    """

    port_name: str = "python-d1-synth"
    timeout_seconds: float = 60.0

    def __post_init__(self) -> None:
        if not self.port_name.strip():
            raise ValueError("port_name must not be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


@dataclass(frozen=True)
class VirtualMidiPortResult:
    """Result from opening a bounded virtual MIDI input port.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-027
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-027 Virtual MIDI Port Voor Logic/DAW
    - Version: 0.1.0
    """

    port_name: str
    opened: bool
    message: str


@dataclass(frozen=True)
class MidiAudioTriggerSettings:
    """Settings for bounded external MIDI to audio triggering.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-028
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-028 External MIDI Audio Trigger Integratie
    - Version: 0.1.0
    """

    input_name: str
    max_messages: int = 10
    timeout_seconds: float = 5.0
    sample_rate: int = 44100
    waveform: Waveform = Waveform.SINE
    amplitude: float = 0.2
    channel: OutputChannel = OutputChannel.STEREO
    audio_device: int | str | None = None

    def __post_init__(self) -> None:
        if not self.input_name.strip():
            raise ValueError("input_name must not be empty")
        if self.max_messages <= 0:
            raise ValueError("max_messages must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if not 0 < self.amplitude <= 1.0:
            raise ValueError("amplitude must be between 0 and 1")


@dataclass(frozen=True)
class MidiAudioTriggerResult:
    """Result from bounded external MIDI to audio triggering.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-028
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-028 External MIDI Audio Trigger Integratie
    - Version: 0.1.0
    """

    input_name: str
    received_message_count: int
    played_event_count: int
    audio_frame_count: int
    sample_rate: int
    message: str


@dataclass(frozen=True)
class VirtualMidiAudioTriggerSettings:
    """Settings for bounded Logic/DAW virtual MIDI to audio triggering.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-029
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-029 Logic/DAW Virtual MIDI Naar Audio Trigger
    - Version: 0.1.0
    """

    port_name: str = "python-d1-synth"
    max_messages: int = 10
    timeout_seconds: float = 30.0
    sample_rate: int = 44100
    waveform: Waveform = Waveform.SINE
    amplitude: float = 0.2
    channel: OutputChannel = OutputChannel.STEREO
    audio_device: int | str | None = None

    def __post_init__(self) -> None:
        if not self.port_name.strip():
            raise ValueError("port_name must not be empty")
        if self.max_messages <= 0:
            raise ValueError("max_messages must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if not 0 < self.amplitude <= 1.0:
            raise ValueError("amplitude must be between 0 and 1")


@dataclass(frozen=True)
class VirtualMidiAudioTriggerResult:
    """Result from bounded Logic/DAW virtual MIDI to audio triggering.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-029
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-029 Logic/DAW Virtual MIDI Naar Audio Trigger
    - User Story: US-030 Logic MIDI Region Multi-Note Playback
    - Version: 0.1.0
    """

    port_name: str
    received_message_count: int
    played_event_count: int
    audio_frame_count: int
    sample_rate: int
    message: str
    received_messages: tuple[MidiMessage, ...] = tuple()
    played_events: tuple[NoteEvent, ...] = tuple()


class StreamingVoiceMode(str, Enum):
    """Voice duration mode for streaming MIDI playback.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-033
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-033 Note Off Gated Voice Duration
    - User Story: US-035 Sustained Note Audio Engine
    - User Story: US-036 MIDI Pitch Bend Mapping En DSP
    - User Story: US-037 MIDI Modulation CC1 Mapping En DSP
    - User Story: US-038 Performance Mode Until Interrupt
    - User Story: US-039 Sustain Pedal CC64
    - User Story: US-040 Envelope Release / Soft Note-Off
    - User Story: US-041 Amp Envelope ADSR Parameters
    - Version: 0.1.0
    """

    FIXED = "fixed"
    GATED = "gated"
    SUSTAINED = "sustained"


class PitchBendChannelMode(str, Enum):
    """Pitch bend routing mode for sustained MIDI playback.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-036-IMPEDIMENT-001
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-036 MIDI Pitch Bend Mapping En DSP
    - Version: 0.1.0
    """

    SAME = "same"
    OMNI = "omni"


@dataclass(frozen=True)
class StreamingMidiAudioTriggerSettings:
    """Settings for near-realtime virtual MIDI streaming playback.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-031
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-031 Live/Streaming MIDI Playback Loop
    - User Story: US-032 Duplicate MIDI Event Guard
    - User Story: US-033 Note Off Gated Voice Duration
    - User Story: US-034 Polyphonic Voice Mixer En Triads
    - User Story: US-035 Sustained Note Audio Engine
    - User Story: US-036 MIDI Pitch Bend Mapping En DSP
    - User Story: US-037 MIDI Modulation CC1 Mapping En DSP
    - User Story: US-038 Performance Mode Until Interrupt
    - User Story: US-039 Sustain Pedal CC64
    - User Story: US-040 Envelope Release / Soft Note-Off
    - User Story: US-041 Amp Envelope ADSR Parameters
    - Version: 0.1.0
    """

    port_name: str = "python-d1-synth"
    max_messages: int = 32
    timeout_seconds: float = 30.0
    poll_interval_seconds: float = 0.005
    note_duration_seconds: float = 0.25
    voice_mode: StreamingVoiceMode = StreamingVoiceMode.FIXED
    dedupe_window_seconds: float = 0.03
    chord_window_seconds: float = 0.02
    pitch_bend_range_semitones: float = 2.0
    pitch_bend_channel_mode: PitchBendChannelMode = PitchBendChannelMode.SAME
    max_control_messages: int = 1024
    modulation_vibrato_depth_semitones: float = 0.25
    modulation_vibrato_rate_hz: float = 5.0
    run_until_interrupted: bool = False
    attack_time_seconds: float = 0.0
    decay_time_seconds: float = 0.0
    sustain_level: float = 1.0
    release_time_seconds: float = 0.03
    sample_rate: int = 44100
    waveform: Waveform = Waveform.SINE
    amplitude: float = 0.2
    channel: OutputChannel = OutputChannel.STEREO
    audio_device: int | str | None = None

    def __post_init__(self) -> None:
        if not self.port_name.strip():
            raise ValueError("port_name must not be empty")
        if self.max_messages <= 0:
            raise ValueError("max_messages must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be positive")
        if self.note_duration_seconds <= 0:
            raise ValueError("note_duration_seconds must be positive")
        if not isinstance(self.voice_mode, StreamingVoiceMode):
            raise ValueError("voice_mode must be a StreamingVoiceMode")
        if self.dedupe_window_seconds <= 0:
            raise ValueError("dedupe_window_seconds must be positive")
        if self.chord_window_seconds <= 0:
            raise ValueError("chord_window_seconds must be positive")
        if self.pitch_bend_range_semitones <= 0:
            raise ValueError("pitch_bend_range_semitones must be positive")
        if not isinstance(self.pitch_bend_channel_mode, PitchBendChannelMode):
            raise ValueError("pitch_bend_channel_mode must be a PitchBendChannelMode")
        if self.max_control_messages < 0:
            raise ValueError("max_control_messages must not be negative")
        if self.modulation_vibrato_depth_semitones < 0:
            raise ValueError("modulation_vibrato_depth_semitones must not be negative")
        if self.modulation_vibrato_rate_hz <= 0:
            raise ValueError("modulation_vibrato_rate_hz must be positive")
        if self.attack_time_seconds < 0:
            raise ValueError("attack_time_seconds must not be negative")
        if self.decay_time_seconds < 0:
            raise ValueError("decay_time_seconds must not be negative")
        if not 0 <= self.sustain_level <= 1.0:
            raise ValueError("sustain_level must be between 0 and 1")
        if self.release_time_seconds < 0:
            raise ValueError("release_time_seconds must not be negative")
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if not 0 < self.amplitude <= 1.0:
            raise ValueError("amplitude must be between 0 and 1")


@dataclass(frozen=True)
class StreamingMidiAudioTriggerResult:
    """Result from near-realtime virtual MIDI streaming playback.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-031
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-031 Live/Streaming MIDI Playback Loop
    - User Story: US-032 Duplicate MIDI Event Guard
    - User Story: US-033 Note Off Gated Voice Duration
    - User Story: US-034 Polyphonic Voice Mixer En Triads
    - User Story: US-035 Sustained Note Audio Engine
    - User Story: US-036 MIDI Pitch Bend Mapping En DSP
    - User Story: US-037 MIDI Modulation CC1 Mapping En DSP
    - User Story: US-038 Performance Mode Until Interrupt
    - User Story: US-039 Sustain Pedal CC64
    - User Story: US-040 Envelope Release / Soft Note-Off
    - User Story: US-041 Amp Envelope ADSR Parameters
    - Version: 0.1.0
    """

    port_name: str
    received_message_count: int
    played_event_count: int
    audio_frame_count: int
    sample_rate: int
    message: str
    received_messages: tuple[MidiMessage, ...] = tuple()
    played_events: tuple[NoteEvent, ...] = tuple()
    suppressed_duplicate_count: int = 0


@dataclass(frozen=True)
class DuplicateMidiEventGuardSettings:
    """Settings for suppressing duplicate MIDI echoes in a short time window.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-032
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-032 Duplicate MIDI Event Guard
    - Version: 0.1.0
    """

    window_seconds: float = 0.03

    def __post_init__(self) -> None:
        if self.window_seconds <= 0:
            raise ValueError("window_seconds must be positive")


class DuplicateMidiEventGuard:
    """Suppress identical MIDI messages repeated by DAW/CoreMIDI echo routes.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-032
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-032 Duplicate MIDI Event Guard
    - Version: 0.1.0
    """

    def __init__(self, settings: DuplicateMidiEventGuardSettings | None = None) -> None:
        self._settings = settings if settings is not None else DuplicateMidiEventGuardSettings()
        self._last_seen_time_by_key: dict[tuple[str, int, int, int, int, int, int], float] = {}

    def is_duplicate(self, message: MidiMessage) -> bool:
        key = (
            message.message_type,
            message.note_number,
            message.velocity,
            message.channel,
            message.pitch_bend_value,
            message.control_number,
            message.control_value,
        )
        previous_time = self._last_seen_time_by_key.get(key)
        self._last_seen_time_by_key[key] = message.time_seconds
        if previous_time is None:
            return False
        delta_seconds = message.time_seconds - previous_time
        return 0 <= delta_seconds <= self._settings.window_seconds


@dataclass(frozen=True)
class MidiPitchBendMapper:
    """Map raw MIDI pitch bend values to semitone offsets and frequency ratios.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-036
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-036 MIDI Pitch Bend Mapping En DSP
    - Version: 0.1.0
    """

    bend_range_semitones: float = 2.0

    def __post_init__(self) -> None:
        if self.bend_range_semitones <= 0:
            raise ValueError("bend_range_semitones must be positive")

    def semitones_for(self, pitch_bend_value: int) -> float:
        if not -8192 <= pitch_bend_value <= 8191:
            raise ValueError("pitch_bend_value must be between -8192 and 8191")
        if pitch_bend_value < 0:
            return self.bend_range_semitones * (pitch_bend_value / 8192.0)
        return self.bend_range_semitones * (pitch_bend_value / 8191.0)

    def frequency_ratio_for(self, pitch_bend_value: int) -> float:
        return math.pow(2.0, self.semitones_for(pitch_bend_value) / 12.0)


@dataclass(frozen=True)
class MidiModulationMapper:
    """Map MIDI CC1 modulation values to vibrato depth.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-037
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-037 MIDI Modulation CC1 Mapping En DSP
    - Version: 0.1.0
    """

    max_depth_semitones: float = 0.25

    def __post_init__(self) -> None:
        if self.max_depth_semitones < 0:
            raise ValueError("max_depth_semitones must not be negative")

    def depth_for(self, control_value: int) -> float:
        if not 0 <= control_value <= 127:
            raise ValueError("control_value must be between 0 and 127")
        return self.max_depth_semitones * (control_value / 127.0)


class MidiInputBackend(Protocol):
    def receive_messages(
        self, input_name: str, max_messages: int, timeout_seconds: float
    ) -> tuple[MidiMessage, ...]:
        ...


class VirtualMidiPortBackend(Protocol):
    def open_virtual_input(self, port_name: str, timeout_seconds: float) -> VirtualMidiPortResult:
        ...


class AudioPlayer(Protocol):
    def play(self, buffer: AudioBuffer, device: int | str | None = None) -> None:
        ...


class SustainedAudioPlayer(Protocol):
    def start(self, settings: SustainedAudioPlayerSettings) -> None:
        ...

    def note_on(self, voice_id: tuple[int, int], frequency_hz: float, velocity: float) -> None:
        ...

    def note_off(self, voice_id: tuple[int, int]) -> None:
        ...

    def pitch_bend(self, channel: int, semitones: float) -> None:
        ...

    def modulation(self, channel: int, depth_semitones: float, rate_hz: float) -> None:
        ...

    def stop(self) -> int:
        ...

    def abort(self) -> int:
        ...


class StreamingMidiInputBackend(Protocol):
    def iter_messages(
        self,
        input_name: str,
        max_messages: int,
        timeout_seconds: float,
        poll_interval_seconds: float,
    ) -> Iterable[MidiMessage]:
        ...


class MidiMessageNormalizer:
    """Normalize backend-specific note messages into project MIDI messages.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-026
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-026 Live MIDI Input Receive Loop
    - User Story: US-030 Logic MIDI Region Multi-Note Playback
    - User Story: US-036 MIDI Pitch Bend Mapping En DSP
    - User Story: US-037 MIDI Modulation CC1 Mapping En DSP
    - Version: 0.1.0
    """

    def normalize(self, raw_message, fallback_time_seconds: float | None = None) -> MidiMessage | None:
        message_type = getattr(raw_message, "type", "")
        if message_type not in {"note_on", "note_off", "pitchwheel", "control_change"}:
            return None
        raw_time = float(getattr(raw_message, "time", 0.0))
        time_seconds = fallback_time_seconds if raw_time == 0.0 and fallback_time_seconds is not None else raw_time
        channel = int(getattr(raw_message, "channel", 0)) + 1
        if message_type == "pitchwheel":
            return MidiMessage(
                message_type="pitch_bend",
                note_number=0,
                velocity=0,
                channel=channel,
                time_seconds=time_seconds,
                pitch_bend_value=int(getattr(raw_message, "pitch")),
            )
        if message_type == "control_change":
            return MidiMessage(
                message_type="control_change",
                note_number=0,
                velocity=0,
                channel=channel,
                time_seconds=time_seconds,
                control_number=int(getattr(raw_message, "control")),
                control_value=int(getattr(raw_message, "value")),
            )
        return MidiMessage(
            message_type=message_type,
            note_number=int(getattr(raw_message, "note")),
            velocity=int(getattr(raw_message, "velocity", 0)),
            channel=channel,
            time_seconds=time_seconds,
        )


class MidoMidiInputBackend:
    """Bounded adapter around mido input ports for future hardware tests.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-026
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-026 Live MIDI Input Receive Loop
    - Version: 0.1.0
    """

    def __init__(self, normalizer: MidiMessageNormalizer | None = None) -> None:
        self._normalizer = normalizer if normalizer is not None else MidiMessageNormalizer()

    def receive_messages(
        self, input_name: str, max_messages: int, timeout_seconds: float
    ) -> tuple[MidiMessage, ...]:
        try:
            import mido
        except ImportError as exc:
            raise RuntimeError("MIDI backend is not available. Install the midi extras first.") from exc

        received: list[MidiMessage] = []
        start_time = time.monotonic()
        deadline = start_time + timeout_seconds
        with mido.open_input(input_name) as port:
            while len(received) < max_messages and time.monotonic() < deadline:
                elapsed_seconds = time.monotonic() - start_time
                for raw_message in port.iter_pending():
                    message = self._normalizer.normalize(raw_message, fallback_time_seconds=elapsed_seconds)
                    if message is not None:
                        received.append(message)
                    if len(received) >= max_messages:
                        break
                time.sleep(0.01)
        return tuple(received)


class MidoVirtualMidiInputBackend:
    """Bounded adapter around a mido virtual input port for Logic/DAW notes.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-029
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-029 Logic/DAW Virtual MIDI Naar Audio Trigger
    - User Story: US-030 Logic MIDI Region Multi-Note Playback
    - Version: 0.1.0
    """

    def __init__(self, normalizer: MidiMessageNormalizer | None = None) -> None:
        self._normalizer = normalizer if normalizer is not None else MidiMessageNormalizer()

    def receive_messages(
        self, input_name: str, max_messages: int, timeout_seconds: float
    ) -> tuple[MidiMessage, ...]:
        try:
            import mido
        except ImportError as exc:
            raise RuntimeError("MIDI backend is not available. Install the midi extras first.") from exc

        received: list[MidiMessage] = []
        start_time = time.monotonic()
        deadline = start_time + timeout_seconds
        try:
            with mido.open_input(input_name, virtual=True) as port:
                while len(received) < max_messages and time.monotonic() < deadline:
                    elapsed_seconds = time.monotonic() - start_time
                    for raw_message in port.iter_pending():
                        message = self._normalizer.normalize(raw_message, fallback_time_seconds=elapsed_seconds)
                        if message is not None:
                            received.append(message)
                        if len(received) >= max_messages:
                            break
                    time.sleep(0.01)
        except TypeError as exc:
            raise RuntimeError(
                "Virtual MIDI input could not be opened because the active mido backend does not support "
                "virtual=True for input ports."
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                "Virtual MIDI input could not be opened. Check the mido/python-rtmidi backend and macOS "
                "CoreMIDI permissions."
            ) from exc
        return tuple(received)


class MidoStreamingVirtualMidiInputBackend:
    """Stream note messages from a mido virtual input port as they arrive.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-031
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-031 Live/Streaming MIDI Playback Loop
    - User Story: US-034 Polyphonic Voice Mixer En Triads
    - Version: 0.1.0
    """

    def __init__(self, normalizer: MidiMessageNormalizer | None = None) -> None:
        self._normalizer = normalizer if normalizer is not None else MidiMessageNormalizer()

    def iter_messages(
        self,
        input_name: str,
        max_messages: int,
        timeout_seconds: float,
        poll_interval_seconds: float,
    ) -> Iterable[MidiMessage]:
        try:
            import mido
        except ImportError as exc:
            raise RuntimeError("MIDI backend is not available. Install the midi extras first.") from exc

        yielded = 0
        start_time = time.monotonic()
        deadline = start_time + timeout_seconds
        try:
            with mido.open_input(input_name, virtual=True) as port:
                while yielded < max_messages and time.monotonic() < deadline:
                    elapsed_seconds = time.monotonic() - start_time
                    for raw_message in port.iter_pending():
                        message = self._normalizer.normalize(raw_message, fallback_time_seconds=elapsed_seconds)
                        if message is not None:
                            yielded += 1
                            yield message
                        if yielded >= max_messages:
                            break
                    time.sleep(poll_interval_seconds)
        except TypeError as exc:
            raise RuntimeError(
                "Streaming virtual MIDI input could not be opened because the active mido backend does not support "
                "virtual=True for input ports."
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                "Streaming virtual MIDI input could not be opened. Check the mido/python-rtmidi backend and macOS "
                "CoreMIDI permissions."
            ) from exc

    def iter_message_batches(
        self,
        input_name: str,
        max_messages: int,
        timeout_seconds: float,
        poll_interval_seconds: float,
    ) -> Iterable[tuple[MidiMessage, ...]]:
        try:
            import mido
        except ImportError as exc:
            raise RuntimeError("MIDI backend is not available. Install the midi extras first.") from exc

        yielded = 0
        start_time = time.monotonic()
        deadline = start_time + timeout_seconds
        try:
            with mido.open_input(input_name, virtual=True) as port:
                while yielded < max_messages and time.monotonic() < deadline:
                    elapsed_seconds = time.monotonic() - start_time
                    batch: list[MidiMessage] = []
                    for raw_message in port.iter_pending():
                        message = self._normalizer.normalize(raw_message, fallback_time_seconds=elapsed_seconds)
                        if message is not None:
                            yielded += 1
                            batch.append(message)
                        if yielded >= max_messages:
                            break
                    if batch:
                        yield tuple(batch)
                    time.sleep(poll_interval_seconds)
        except TypeError as exc:
            raise RuntimeError(
                "Streaming virtual MIDI input could not be opened because the active mido backend does not support "
                "virtual=True for input ports."
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                "Streaming virtual MIDI input could not be opened. Check the mido/python-rtmidi backend and macOS "
                "CoreMIDI permissions."
            ) from exc


class MidoVirtualMidiPortBackend:
    """Open a bounded mido virtual input port for Logic/DAW visibility tests.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-027
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-027 Virtual MIDI Port Voor Logic/DAW
    - Version: 0.1.0
    """

    def open_virtual_input(self, port_name: str, timeout_seconds: float) -> VirtualMidiPortResult:
        try:
            import mido
        except ImportError as exc:
            raise RuntimeError("MIDI backend is not available. Install the midi extras first.") from exc

        try:
            with mido.open_input(port_name, virtual=True):
                time.sleep(timeout_seconds)
        except TypeError as exc:
            raise RuntimeError(
                "Virtual MIDI port could not be opened because the active mido backend does not support "
                "virtual=True for input ports."
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                "Virtual MIDI port could not be opened. Check the mido/python-rtmidi backend and macOS "
                "CoreMIDI permissions."
            ) from exc

        return VirtualMidiPortResult(
            port_name=port_name,
            opened=True,
            message=f"Virtual MIDI input port opened: {port_name}.",
        )


class VirtualMidiPortManager:
    """Manage the lifecycle of a bounded virtual MIDI input port.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-027
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-027 Virtual MIDI Port Voor Logic/DAW
    - Version: 0.1.0
    """

    def __init__(self, backend: VirtualMidiPortBackend | None = None) -> None:
        self._backend = backend if backend is not None else MidoVirtualMidiPortBackend()

    def open(self, settings: VirtualMidiPortSettings) -> VirtualMidiPortResult:
        return self._backend.open_virtual_input(settings.port_name, settings.timeout_seconds)


class LiveMidiInputReceiver:
    """Run a bounded MIDI receive loop and map note messages to NoteSequence.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-026
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-026 Live MIDI Input Receive Loop
    - Version: 0.1.0
    """

    def __init__(
        self,
        backend: MidiInputBackend | None = None,
        mapper: MidiToNoteEventMapper | None = None,
    ) -> None:
        self._backend = backend if backend is not None else MidoMidiInputBackend()
        self._mapper = mapper if mapper is not None else MidiToNoteEventMapper()

    def receive(self, settings: MidiInputReceiveSettings) -> MidiInputReceiveResult:
        messages = self._backend.receive_messages(
            settings.input_name,
            settings.max_messages,
            settings.timeout_seconds,
        )
        sequence = self._mapper.messages_to_note_sequence(messages)
        return MidiInputReceiveResult(
            input_name=settings.input_name,
            received_messages=messages,
            note_sequence=sequence,
            message=f"Received {len(messages)} MIDI note messages from {settings.input_name}.",
        )


class MidiAudioTrigger:
    """Receive bounded MIDI note events, render them, and play one audio buffer.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-028
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-028 External MIDI Audio Trigger Integratie
    - Version: 0.1.0
    """

    def __init__(
        self,
        receiver: LiveMidiInputReceiver | None = None,
        audio_player: AudioPlayer | None = None,
    ) -> None:
        self._receiver = receiver if receiver is not None else LiveMidiInputReceiver()
        self._audio_player = audio_player if audio_player is not None else SoundDeviceAudioPlayer()

    def trigger(self, settings: MidiAudioTriggerSettings) -> MidiAudioTriggerResult:
        receive_result = self._receiver.receive(
            MidiInputReceiveSettings(
                input_name=settings.input_name,
                max_messages=settings.max_messages,
                timeout_seconds=settings.timeout_seconds,
            )
        )
        event_count = len(receive_result.note_sequence.events)
        if event_count == 0:
            return MidiAudioTriggerResult(
                input_name=settings.input_name,
                received_message_count=len(receive_result.received_messages),
                played_event_count=0,
                audio_frame_count=0,
                sample_rate=settings.sample_rate,
                message=f"Received 0 MIDI-triggered note events from {settings.input_name}; no audio played.",
            )

        engine = SynthEngine(
            SynthEngineSettings(
                sample_rate=settings.sample_rate,
                waveform=settings.waveform,
                amplitude=settings.amplitude,
                channel=settings.channel,
            )
        )
        buffer = engine.render_sequence(receive_result.note_sequence)
        self._audio_player.play(buffer, device=settings.audio_device)
        return MidiAudioTriggerResult(
            input_name=settings.input_name,
            received_message_count=len(receive_result.received_messages),
            played_event_count=event_count,
            audio_frame_count=buffer.samples.shape[0],
            sample_rate=buffer.sample_rate,
            message=f"Played {event_count} MIDI-triggered note events from {settings.input_name}.",
        )


class VirtualMidiAudioTrigger:
    """Open a virtual MIDI input port, receive DAW notes, and play audio.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-029
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-029 Logic/DAW Virtual MIDI Naar Audio Trigger
    - User Story: US-030 Logic MIDI Region Multi-Note Playback
    - Version: 0.1.0
    """

    def __init__(
        self,
        receiver: LiveMidiInputReceiver | None = None,
        audio_player: AudioPlayer | None = None,
    ) -> None:
        self._receiver = (
            receiver if receiver is not None else LiveMidiInputReceiver(backend=MidoVirtualMidiInputBackend())
        )
        self._audio_player = audio_player if audio_player is not None else SoundDeviceAudioPlayer()

    def trigger(self, settings: VirtualMidiAudioTriggerSettings) -> VirtualMidiAudioTriggerResult:
        receive_result = self._receiver.receive(
            MidiInputReceiveSettings(
                input_name=settings.port_name,
                max_messages=settings.max_messages,
                timeout_seconds=settings.timeout_seconds,
            )
        )
        event_count = len(receive_result.note_sequence.events)
        if event_count == 0:
            return VirtualMidiAudioTriggerResult(
                port_name=settings.port_name,
                received_message_count=len(receive_result.received_messages),
                played_event_count=0,
                audio_frame_count=0,
                sample_rate=settings.sample_rate,
                message=(
                    f"Received {len(receive_result.received_messages)} MIDI note messages from virtual MIDI port "
                    f"{settings.port_name}; no audio played."
                ),
                received_messages=receive_result.received_messages,
                played_events=tuple(),
            )

        played_events = receive_result.note_sequence.events
        engine = SynthEngine(
            SynthEngineSettings(
                sample_rate=settings.sample_rate,
                waveform=settings.waveform,
                amplitude=settings.amplitude,
                channel=settings.channel,
            )
        )
        buffer = engine.render_sequence(receive_result.note_sequence)
        self._audio_player.play(buffer, device=settings.audio_device)
        return VirtualMidiAudioTriggerResult(
            port_name=settings.port_name,
            received_message_count=len(receive_result.received_messages),
            played_event_count=event_count,
            audio_frame_count=buffer.samples.shape[0],
            sample_rate=buffer.sample_rate,
            message=f"Played {event_count} MIDI-triggered note events from virtual MIDI port {settings.port_name}.",
            received_messages=receive_result.received_messages,
            played_events=played_events,
        )


class StreamingMidiAudioTrigger:
    """Play received virtual MIDI note_on messages as mono or chord audio buffers.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-031
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-031 Live/Streaming MIDI Playback Loop
    - User Story: US-032 Duplicate MIDI Event Guard
    - User Story: US-033 Note Off Gated Voice Duration
    - User Story: US-034 Polyphonic Voice Mixer En Triads
    - User Story: US-035 Sustained Note Audio Engine
    - User Story: US-036 MIDI Pitch Bend Mapping En DSP
    - User Story: US-037 MIDI Modulation CC1 Mapping En DSP
    - User Story: US-038 Performance Mode Until Interrupt
    - User Story: US-039 Sustain Pedal CC64
    - User Story: US-040 Envelope Release / Soft Note-Off
    - User Story: US-041 Amp Envelope ADSR Parameters
    - Version: 0.1.0
    """

    def __init__(
        self,
        backend: StreamingMidiInputBackend | None = None,
        audio_player: AudioPlayer | None = None,
        sustained_audio_player: SustainedAudioPlayer | None = None,
        duplicate_guard: DuplicateMidiEventGuard | None = None,
    ) -> None:
        self._backend = backend if backend is not None else MidoStreamingVirtualMidiInputBackend()
        self._audio_player = audio_player if audio_player is not None else SoundDeviceAudioPlayer()
        self._sustained_audio_player = (
            sustained_audio_player if sustained_audio_player is not None else SoundDeviceSustainedAudioPlayer()
        )
        self._duplicate_guard = duplicate_guard

    def trigger(self, settings: StreamingMidiAudioTriggerSettings) -> StreamingMidiAudioTriggerResult:
        engine = SynthEngine(
            SynthEngineSettings(
                sample_rate=settings.sample_rate,
                waveform=settings.waveform,
                amplitude=settings.amplitude,
                channel=settings.channel,
            )
        )
        mapper = MidiToNoteEventMapper(default_note_duration_seconds=settings.note_duration_seconds)
        duplicate_guard = self._duplicate_guard
        if duplicate_guard is None:
            duplicate_guard = DuplicateMidiEventGuard(
                DuplicateMidiEventGuardSettings(window_seconds=settings.dedupe_window_seconds)
            )

        if settings.voice_mode is StreamingVoiceMode.GATED:
            return self._trigger_gated(settings, engine, mapper, duplicate_guard)
        if settings.voice_mode is StreamingVoiceMode.SUSTAINED:
            return self._trigger_sustained(settings, mapper, duplicate_guard)
        return self._trigger_fixed(settings, engine, mapper, duplicate_guard)

    def _trigger_fixed(
        self,
        settings: StreamingMidiAudioTriggerSettings,
        engine: SynthEngine,
        mapper: MidiToNoteEventMapper,
        duplicate_guard: DuplicateMidiEventGuard,
    ) -> StreamingMidiAudioTriggerResult:
        received_messages: list[MidiMessage] = []
        played_events: list[NoteEvent] = []
        audio_frame_count = 0
        suppressed_duplicate_count = 0

        for message_batch in self._iter_message_batches(settings):
            batch_messages, suppressed_count = self._filter_duplicate_messages(message_batch, duplicate_guard)
            received_messages.extend(message_batch)
            suppressed_duplicate_count += suppressed_count

            batch_events = self._events_from_note_on_messages(mapper, batch_messages)
            for event_group in self._group_chord_events(batch_events, settings.chord_window_seconds):
                audio_frame_count += self._play_events(engine, event_group, settings.audio_device)
                played_events.extend(event_group)

        return self._streaming_result(
            settings=settings,
            received_messages=received_messages,
            played_events=played_events,
            audio_frame_count=audio_frame_count,
            suppressed_duplicate_count=suppressed_duplicate_count,
        )

    def _trigger_gated(
        self,
        settings: StreamingMidiAudioTriggerSettings,
        engine: SynthEngine,
        mapper: MidiToNoteEventMapper,
        duplicate_guard: DuplicateMidiEventGuard,
    ) -> StreamingMidiAudioTriggerResult:
        received_messages: list[MidiMessage] = []
        played_events: list[NoteEvent] = []
        active_note_on_by_key: dict[tuple[int, int], tuple[MidiMessage, int]] = {}
        audio_frame_count = 0
        suppressed_duplicate_count = 0

        for message_batch in self._iter_message_batches(settings):
            batch_messages, suppressed_count = self._filter_duplicate_messages(message_batch, duplicate_guard)
            received_messages.extend(message_batch)
            suppressed_duplicate_count += suppressed_count
            pending_events_to_play: list[NoteEvent] = []

            for message in batch_messages:
                key = (message.channel, message.note_number)
                if message.message_type == "note_on" and message.velocity > 0:
                    previous_active_note = active_note_on_by_key.get(key)
                    if previous_active_note is not None:
                        previous_note_on, previous_event_index = previous_active_note
                        played_events[previous_event_index] = self._gated_event_from_messages(
                            mapper, previous_note_on, message, settings
                        )
                    event = self._fallback_event_from_note_on(mapper, message, settings)
                    pending_events_to_play.append(event)
                    played_events.append(event)
                    active_note_on_by_key[key] = (message, len(played_events) - 1)
                    continue

                active_note = active_note_on_by_key.pop(key, None)
                if active_note is None:
                    continue
                note_on, event_index = active_note
                played_events[event_index] = self._gated_event_from_messages(mapper, note_on, message, settings)

            for event_group in self._group_chord_events(tuple(pending_events_to_play), settings.chord_window_seconds):
                audio_frame_count += self._play_events(engine, event_group, settings.audio_device)

        return self._streaming_result(
            settings=settings,
            received_messages=received_messages,
            played_events=played_events,
            audio_frame_count=audio_frame_count,
            suppressed_duplicate_count=suppressed_duplicate_count,
        )

    def _trigger_sustained(
        self,
        settings: StreamingMidiAudioTriggerSettings,
        mapper: MidiToNoteEventMapper,
        duplicate_guard: DuplicateMidiEventGuard,
    ) -> StreamingMidiAudioTriggerResult:
        received_messages: list[MidiMessage] = []
        played_events: list[NoteEvent] = []
        active_note_on_by_key: dict[tuple[int, int], tuple[MidiMessage, int]] = {}
        suppressed_duplicate_count = 0
        sustained_player = self._sustained_audio_player
        pitch_bend_mapper = MidiPitchBendMapper(settings.pitch_bend_range_semitones)
        modulation_mapper = MidiModulationMapper(settings.modulation_vibrato_depth_semitones)
        pitch_bend_by_channel: dict[int, float] = {}
        modulation_depth_by_channel: dict[int, float] = {}
        sustain_down_by_channel: dict[int, bool] = {}
        sustained_release_keys: set[tuple[int, int]] = set()
        omni_pitch_bend_semitones: float | None = None
        interrupted = False

        sustained_player.start(
            SustainedAudioPlayerSettings(
                sample_rate=settings.sample_rate,
                waveform=settings.waveform,
                amplitude=settings.amplitude,
                channel=settings.channel,
                device=settings.audio_device,
                attack_seconds=settings.attack_time_seconds,
                decay_seconds=settings.decay_time_seconds,
                sustain_level=settings.sustain_level,
                release_seconds=settings.release_time_seconds,
            )
        )
        try:
            for message_batch in self._iter_message_batches(settings):
                batch_messages, suppressed_count = self._filter_duplicate_messages(message_batch, duplicate_guard)
                received_messages.extend(message_batch)
                suppressed_duplicate_count += suppressed_count

                for message in batch_messages:
                    key = (message.channel, message.note_number)
                    if message.message_type == "pitch_bend":
                        semitones = pitch_bend_mapper.semitones_for(message.pitch_bend_value)
                        if settings.pitch_bend_channel_mode is PitchBendChannelMode.OMNI:
                            omni_pitch_bend_semitones = semitones
                            active_channels = {active_channel for active_channel, _note_number in active_note_on_by_key}
                            for active_channel in active_channels:
                                sustained_player.pitch_bend(active_channel, semitones)
                        else:
                            pitch_bend_by_channel[message.channel] = semitones
                            sustained_player.pitch_bend(message.channel, semitones)
                        continue
                    if message.message_type == "control_change":
                        if message.control_number == 1:
                            depth = modulation_mapper.depth_for(message.control_value)
                            modulation_depth_by_channel[message.channel] = depth
                            sustained_player.modulation(
                                message.channel,
                                depth,
                                settings.modulation_vibrato_rate_hz,
                            )
                            continue
                        if message.control_number == 64:
                            sustain_down = message.control_value >= 64
                            sustain_down_by_channel[message.channel] = sustain_down
                            if not sustain_down:
                                for released_key in self._release_sustained_keys_for_channel(
                                    message.channel,
                                    message,
                                    active_note_on_by_key,
                                    sustained_release_keys,
                                    played_events,
                                    mapper,
                                    settings,
                                ):
                                    sustained_player.note_off(released_key)
                            continue
                        continue
                    if message.message_type == "note_on" and message.velocity > 0:
                        previous_active_note = active_note_on_by_key.get(key)
                        if previous_active_note is not None:
                            previous_note_on, previous_event_index = previous_active_note
                            played_events[previous_event_index] = self._gated_event_from_messages(
                                mapper, previous_note_on, message, settings
                            )
                            sustained_release_keys.discard(key)
                        event = self._fallback_event_from_note_on(mapper, message, settings)
                        sustained_player.note_on(key, event.note.frequency_hz, event.velocity)
                        if settings.pitch_bend_channel_mode is PitchBendChannelMode.OMNI:
                            if omni_pitch_bend_semitones is not None:
                                sustained_player.pitch_bend(message.channel, omni_pitch_bend_semitones)
                        elif message.channel in pitch_bend_by_channel:
                            sustained_player.pitch_bend(message.channel, pitch_bend_by_channel[message.channel])
                        if message.channel in modulation_depth_by_channel:
                            sustained_player.modulation(
                                message.channel,
                                modulation_depth_by_channel[message.channel],
                                settings.modulation_vibrato_rate_hz,
                            )
                        played_events.append(event)
                        active_note_on_by_key[key] = (message, len(played_events) - 1)
                        continue

                    active_note = active_note_on_by_key.pop(key, None)
                    if active_note is None:
                        continue
                    if sustain_down_by_channel.get(message.channel, False):
                        active_note_on_by_key[key] = active_note
                        sustained_release_keys.add(key)
                        continue
                    note_on, event_index = active_note
                    sustained_player.note_off(key)
                    played_events[event_index] = self._gated_event_from_messages(mapper, note_on, message, settings)
        except KeyboardInterrupt:
            interrupted = True
            raise
        finally:
            for key in tuple(active_note_on_by_key):
                sustained_player.note_off(key)
            audio_frame_count = sustained_player.abort() if interrupted else sustained_player.stop()

        return self._streaming_result(
            settings=settings,
            received_messages=received_messages,
            played_events=played_events,
            audio_frame_count=audio_frame_count,
            suppressed_duplicate_count=suppressed_duplicate_count,
        )

    def _release_sustained_keys_for_channel(
        self,
        channel: int,
        release_message: MidiMessage,
        active_note_on_by_key: dict[tuple[int, int], tuple[MidiMessage, int]],
        sustained_release_keys: set[tuple[int, int]],
        played_events: list[NoteEvent],
        mapper: MidiToNoteEventMapper,
        settings: StreamingMidiAudioTriggerSettings,
    ) -> tuple[tuple[int, int], ...]:
        released_keys: list[tuple[int, int]] = []
        for key in tuple(sustained_release_keys):
            key_channel, note_number = key
            if key_channel != channel:
                continue
            active_note = active_note_on_by_key.pop(key, None)
            sustained_release_keys.discard(key)
            if active_note is None:
                continue
            note_on, event_index = active_note
            note_off = MidiMessage(
                message_type="note_off",
                note_number=note_number,
                velocity=release_message.velocity,
                channel=channel,
                time_seconds=release_message.time_seconds,
            )
            played_events[event_index] = self._gated_event_from_messages(mapper, note_on, note_off, settings)
            released_keys.append(key)
        return tuple(released_keys)

    def _gated_event_from_messages(
        self,
        mapper: MidiToNoteEventMapper,
        note_on: MidiMessage,
        closing_message: MidiMessage,
        settings: StreamingMidiAudioTriggerSettings,
    ) -> NoteEvent:
        note_off_time = closing_message.time_seconds
        if note_off_time <= note_on.time_seconds:
            note_off_time = note_on.time_seconds + settings.note_duration_seconds
        note_off = MidiMessage(
            message_type="note_off",
            note_number=note_on.note_number,
            velocity=closing_message.velocity,
            channel=note_on.channel,
            time_seconds=note_off_time,
        )
        sequence = mapper.messages_to_note_sequence((note_on, note_off))
        return sequence.events[0]

    def _fallback_event_from_note_on(
        self,
        mapper: MidiToNoteEventMapper,
        note_on: MidiMessage,
        settings: StreamingMidiAudioTriggerSettings,
    ) -> NoteEvent:
        fallback_note_off = MidiMessage(
            message_type="note_off",
            note_number=note_on.note_number,
            velocity=0,
            channel=note_on.channel,
            time_seconds=note_on.time_seconds + settings.note_duration_seconds,
        )
        return self._gated_event_from_messages(mapper, note_on, fallback_note_off, settings)

    def _play_event(self, engine: SynthEngine, event: NoteEvent, audio_device: int | str | None) -> int:
        buffer = engine.render_note(event)
        self._audio_player.play(buffer, device=audio_device)
        return int(buffer.samples.shape[0])

    def _play_events(self, engine: SynthEngine, events: tuple[NoteEvent, ...], audio_device: int | str | None) -> int:
        if len(events) == 1:
            return self._play_event(engine, events[0], audio_device)
        start_seconds = min(event.start_seconds for event in events)
        chord_events = tuple(
            NoteEvent(
                note=event.note,
                duration_seconds=event.duration_seconds,
                velocity=event.velocity,
                start_seconds=event.start_seconds - start_seconds,
            )
            for event in events
        )
        buffer = engine.render_sequence(NoteSequence(chord_events))
        self._audio_player.play(buffer, device=audio_device)
        return int(buffer.samples.shape[0])

    def _iter_message_batches(
        self,
        settings: StreamingMidiAudioTriggerSettings,
    ) -> Iterable[tuple[MidiMessage, ...]]:
        batch_reader = getattr(self._backend, "iter_message_batches", None)
        backend_message_limit = self._backend_message_limit(settings)
        timeout_seconds = self._backend_timeout_seconds(settings)
        if callable(batch_reader):
            yield from batch_reader(
                settings.port_name,
                backend_message_limit,
                timeout_seconds,
                settings.poll_interval_seconds,
            )
            return
        for message in self._backend.iter_messages(
            settings.port_name,
            backend_message_limit,
            timeout_seconds,
            settings.poll_interval_seconds,
        ):
            yield (message,)

    def _backend_message_limit(self, settings: StreamingMidiAudioTriggerSettings) -> int:
        if settings.run_until_interrupted:
            return sys.maxsize
        return settings.max_messages + settings.max_control_messages

    def _backend_timeout_seconds(self, settings: StreamingMidiAudioTriggerSettings) -> float:
        if settings.run_until_interrupted:
            return 365 * 24 * 60 * 60.0
        return settings.timeout_seconds

    def _filter_duplicate_messages(
        self,
        message_batch: tuple[MidiMessage, ...],
        duplicate_guard: DuplicateMidiEventGuard,
    ) -> tuple[tuple[MidiMessage, ...], int]:
        messages: list[MidiMessage] = []
        suppressed_count = 0
        for message in message_batch:
            if duplicate_guard.is_duplicate(message):
                suppressed_count += 1
                continue
            messages.append(message)
        return tuple(messages), suppressed_count

    def _events_from_note_on_messages(
        self,
        mapper: MidiToNoteEventMapper,
        messages: tuple[MidiMessage, ...],
    ) -> tuple[NoteEvent, ...]:
        events: list[NoteEvent] = []
        for message in messages:
            if message.message_type != "note_on" or message.velocity == 0:
                continue
            sequence = mapper.messages_to_note_sequence((message,))
            if sequence.events:
                events.append(sequence.events[0])
        return tuple(events)

    def _group_chord_events(
        self,
        events: tuple[NoteEvent, ...],
        chord_window_seconds: float,
    ) -> tuple[tuple[NoteEvent, ...], ...]:
        groups: list[tuple[NoteEvent, ...]] = []
        pending_group: list[NoteEvent] = []
        group_start_seconds: float | None = None
        for event in sorted(events, key=lambda item: item.start_seconds):
            if group_start_seconds is None:
                pending_group = [event]
                group_start_seconds = event.start_seconds
                continue
            if event.start_seconds - group_start_seconds <= chord_window_seconds:
                pending_group.append(event)
                continue
            groups.append(tuple(pending_group))
            pending_group = [event]
            group_start_seconds = event.start_seconds
        if pending_group:
            groups.append(tuple(pending_group))
        return tuple(groups)

    def _streaming_result(
        self,
        settings: StreamingMidiAudioTriggerSettings,
        received_messages: list[MidiMessage],
        played_events: list[NoteEvent],
        audio_frame_count: int,
        suppressed_duplicate_count: int,
    ) -> StreamingMidiAudioTriggerResult:
        if not played_events:
            return StreamingMidiAudioTriggerResult(
                port_name=settings.port_name,
                received_message_count=len(received_messages),
                played_event_count=0,
                audio_frame_count=0,
                sample_rate=settings.sample_rate,
                message=(
                    f"Received {len(received_messages)} MIDI note messages from streaming virtual MIDI port "
                    f"{settings.port_name}; no audio played."
                ),
                received_messages=tuple(received_messages),
                played_events=tuple(),
                suppressed_duplicate_count=suppressed_duplicate_count,
            )

        return StreamingMidiAudioTriggerResult(
            port_name=settings.port_name,
            received_message_count=len(received_messages),
            played_event_count=len(played_events),
            audio_frame_count=audio_frame_count,
            sample_rate=settings.sample_rate,
            message=(
                f"Streamed {len(played_events)} MIDI-triggered note events from virtual MIDI port "
                f"{settings.port_name}; suppressed {suppressed_duplicate_count} duplicate MIDI messages."
            ),
            received_messages=tuple(received_messages),
            played_events=tuple(played_events),
            suppressed_duplicate_count=suppressed_duplicate_count,
        )


class UsbMidiHardwareInputAdapter:
    """Diagnose generic USB MIDI input devices before live receive is enabled.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-022
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-022 USB MIDI Hardware Input
    - Version: 0.1.0
    """

    def diagnose(self, devices: tuple[MidiDevice, ...], requested_device: str | None = None) -> UsbMidiInputDiagnostic:
        input_devices = tuple(device for device in devices if device.direction == "input")
        if not input_devices:
            return UsbMidiInputDiagnostic(
                ready=False,
                message=(
                    "No USB MIDI input devices detected. Connect any class-compliant USB MIDI interface and run "
                    "the diagnostic again."
                ),
                selected_device=None,
                compatible_devices=tuple(),
            )

        selected = self._select_device(input_devices, requested_device)
        if selected is None:
            names = ", ".join(device.name for device in input_devices)
            return UsbMidiInputDiagnostic(
                ready=False,
                message=f"Requested USB MIDI input device not found. Available input devices: {names}.",
                selected_device=None,
                compatible_devices=input_devices,
            )

        return UsbMidiInputDiagnostic(
            ready=True,
            message=f"USB MIDI input ready: {selected.name} ({selected.identifier}).",
            selected_device=selected,
            compatible_devices=input_devices,
        )

    def _select_device(self, devices: tuple[MidiDevice, ...], requested_device: str | None) -> MidiDevice | None:
        if requested_device is None:
            return devices[0]
        normalized = requested_device.casefold()
        for device in devices:
            if normalized in device.name.casefold() or normalized == device.identifier.casefold():
                return device
        return None


class MidiToNoteEventMapper:
    """Map device-independent MIDI note messages to the internal note model.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-024
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-024 MIDI Naar NoteEvent Mapping
    - Version: 0.1.0
    """

    def __init__(self, default_note_duration_seconds: float = 1.0) -> None:
        if default_note_duration_seconds <= 0:
            raise ValueError("default_note_duration_seconds must be positive")
        self._default_note_duration_seconds = default_note_duration_seconds
        self._parser = NoteParser()

    def messages_to_note_sequence(self, messages: tuple[MidiMessage, ...]) -> NoteSequence:
        active_notes: dict[tuple[int, int], MidiMessage] = {}
        events: list[NoteEvent] = []

        for message in messages:
            key = (message.channel, message.note_number)
            if message.message_type == "note_on" and message.velocity > 0:
                active_notes[key] = message
                continue

            started = active_notes.pop(key, None)
            if started is not None:
                events.append(self._event_from_pair(started, message))

        for started in active_notes.values():
            events.append(self._event_from_open_note(started))

        return NoteSequence(events=tuple(sorted(events, key=lambda event: event.start_seconds)))

    def _event_from_pair(self, started: MidiMessage, stopped: MidiMessage) -> NoteEvent:
        duration = stopped.time_seconds - started.time_seconds
        if duration <= 0:
            duration = self._default_note_duration_seconds
        return NoteEvent(
            note=self._note_from_midi_number(started.note_number),
            duration_seconds=duration,
            velocity=started.velocity / 127,
            start_seconds=started.time_seconds,
        )

    def _event_from_open_note(self, started: MidiMessage) -> NoteEvent:
        return NoteEvent(
            note=self._note_from_midi_number(started.note_number),
            duration_seconds=self._default_note_duration_seconds,
            velocity=started.velocity / 127,
            start_seconds=started.time_seconds,
        )

    def _note_from_midi_number(self, note_number: int):
        note_names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
        octave = (note_number // 12) - 1
        name = note_names[note_number % 12]
        return self._parser.parse(f"{name}{octave}")


class VirtualMidiInputAdapter:
    """Map virtual MIDI note messages to the internal note sequence model.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-020
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-020 Virtual MIDI Input Voor DAW
    - Version: 0.1.0
    """

    def __init__(self, settings: VirtualMidiInputSettings | None = None) -> None:
        self._settings = settings if settings is not None else VirtualMidiInputSettings()
        self._mapper = MidiToNoteEventMapper(
            default_note_duration_seconds=self._settings.default_note_duration_seconds
        )

    def diagnose(self, backend_available: bool) -> VirtualMidiInputDiagnostic:
        if backend_available:
            return VirtualMidiInputDiagnostic(
                available=True,
                message=(
                    f"Virtual MIDI input backend is installed. Route a DAW track to '{self._settings.input_name}' "
                    "when the live input story opens the port."
                ),
            )
        return VirtualMidiInputDiagnostic(
            available=False,
            message=(
                "Virtual MIDI input backend is not available. Install the MIDI extras and verify a virtual MIDI "
                "route before DAW input."
            ),
        )

    def messages_to_note_sequence(self, messages: tuple[MidiMessage, ...]) -> NoteSequence:
        return self._mapper.messages_to_note_sequence(messages)


class MidiDeviceScanner:
    """Safe MIDI device scanner with macOS CoreMIDI crash isolation.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-022-BLOCKER
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-022 USB MIDI Hardware Input
    - Version: 0.1.0
    """

    _BACKEND_NAME = "mido/python-rtmidi"

    def __init__(self, allow_unsafe_native_scan: bool = False) -> None:
        self._allow_unsafe_native_scan = allow_unsafe_native_scan

    def scan(self) -> MidiDeviceScanResult:
        if platform.system() == "Darwin" and not self._allow_unsafe_native_scan:
            return MidiDeviceScanResult(
                devices=tuple(),
                error_message=(
                    "Native RtMidi/CoreMIDI scanning is disabled by default on macOS because it can abort the "
                    "Python process. Use --unsafe-rtmidi-scan only when you intentionally want to test it."
                ),
                backend_name=self._BACKEND_NAME,
            )
        return self._scan_with_mido_subprocess()

    def list_devices(self) -> tuple[MidiDevice, ...]:
        return self.scan().devices

    def _scan_with_mido_subprocess(self) -> MidiDeviceScanResult:
        scan_code = """
import json
try:
    import mido
except ImportError:
    print(json.dumps([]))
    raise SystemExit(0)

devices = []
for index, name in enumerate(mido.get_input_names()):
    devices.append({"identifier": f"input:{index}", "name": name, "direction": "input"})
for index, name in enumerate(mido.get_output_names()):
    devices.append({"identifier": f"output:{index}", "name": name, "direction": "output"})
print(json.dumps(devices))
"""
        try:
            completed = subprocess.run(
                [sys.executable, "-c", scan_code],
                capture_output=True,
                check=False,
                text=True,
                timeout=5.0,
            )
        except (OSError, subprocess.SubprocessError):
            return MidiDeviceScanResult(
                devices=tuple(),
                error_message="MIDI device scan subprocess failed.",
                backend_name=self._BACKEND_NAME,
            )
        if completed.returncode != 0:
            return MidiDeviceScanResult(
                devices=tuple(),
                error_message="MIDI backend failed while scanning devices.",
                backend_name=self._BACKEND_NAME,
                returncode=completed.returncode,
                stdout=completed.stdout.strip(),
                stderr=completed.stderr.strip(),
            )

        try:
            raw_devices = json.loads(completed.stdout)
        except json.JSONDecodeError:
            return MidiDeviceScanResult(
                devices=tuple(),
                error_message="MIDI backend returned invalid scan data.",
                backend_name=self._BACKEND_NAME,
                returncode=completed.returncode,
                stdout=completed.stdout.strip(),
                stderr=completed.stderr.strip(),
            )

        devices = tuple(
            MidiDevice(
                identifier=str(raw["identifier"]),
                name=str(raw["name"]),
                direction=str(raw["direction"]),
            )
            for raw in raw_devices
            if isinstance(raw, dict)
        )
        return MidiDeviceScanResult(
            devices=devices,
            error_message=None,
            backend_name=self._BACKEND_NAME,
            returncode=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
        )


class MidiDeviceSelector:
    """Choose a MIDI input device from CLI args or YAML defaults.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-025
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-025 MIDI Device Discovery En Default Selection
    - Version: 0.1.0
    """

    def select(self, cli_device: str | None, config_device: str | None) -> MidiDeviceSelection:
        if cli_device:
            return MidiDeviceSelection(selected_device=cli_device, source="cli")
        if config_device:
            return MidiDeviceSelection(selected_device=config_device, source="config")
        return MidiDeviceSelection(selected_device=None, source="none")

    def select_input_device(
        self,
        devices: tuple[MidiDevice, ...],
        cli_device: str | None = None,
        cli_device_id: str | None = None,
        config_device: str | None = None,
    ) -> MidiDeviceSelection:
        input_devices = tuple(device for device in devices if device.direction == "input")
        request, source = self._select_request(cli_device, cli_device_id, config_device)

        if request is None:
            return MidiDeviceSelection(
                selected_device=None,
                source="none",
                matched_device=None,
                message="No MIDI input device selected. Use --midi-device, --midi-device-id or midi.default_input_device.",
                available_input_devices=input_devices,
            )

        if not input_devices:
            return MidiDeviceSelection(
                selected_device=request,
                source=source,
                matched_device=None,
                message="No MIDI input devices available. Run python -m synth midi list-devices first.",
                available_input_devices=input_devices,
            )

        matched = self._match_input_device(input_devices, request, source)
        if matched is None:
            available = ", ".join(f"{device.identifier} {device.name}" for device in input_devices)
            return MidiDeviceSelection(
                selected_device=request,
                source=source,
                matched_device=None,
                message=(
                    "Requested MIDI input device not found. "
                    f"Available input devices: {available}. "
                    "Run python -m synth midi list-devices and choose an input identifier or name."
                ),
                available_input_devices=input_devices,
            )

        return MidiDeviceSelection(
            selected_device=request,
            source=source,
            matched_device=matched,
            message=f"Selected MIDI input device from {source}: {matched.identifier} {matched.name}",
            available_input_devices=input_devices,
        )

    def _select_request(
        self, cli_device: str | None, cli_device_id: str | None, config_device: str | None
    ) -> tuple[str | None, str]:
        if cli_device_id:
            return cli_device_id, "cli-id"
        if cli_device:
            return cli_device, "cli"
        if config_device:
            return config_device, "config"
        return None, "none"

    def _match_input_device(
        self, input_devices: tuple[MidiDevice, ...], request: str, source: str
    ) -> MidiDevice | None:
        normalized = request.casefold()
        for device in input_devices:
            if source == "cli-id" and normalized == device.identifier.casefold():
                return device
            if normalized == device.identifier.casefold() or normalized in device.name.casefold():
                return device
        return None
