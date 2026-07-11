# Bestand: test_traceability.py
# Versienummer: 0.1.0
# Doel: Bewaakt code-traceability voor user stories, epics, backlog en ChatOD.
# Sprint: Future MIDI/DAW
# User-Story: US-036 MIDI Pitch Bend Mapping En DSP
# Actie: US-036-TRACEABILITY-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-036

from synth.audio import (
    ChannelRouter,
    OutputChannel,
    SoundDeviceSustainedAudioPlayer,
    SustainedAudioPlayerSettings,
    SustainedVoiceState,
)
from synth.cli import SynthCli
from synth.debug import DebugLevel, DebugReporter
from synth.engine import PolyphonicVoiceMixer
from synth.midi import (
    DuplicateMidiEventGuard,
    DuplicateMidiEventGuardSettings,
    LiveMidiInputReceiver,
    MidiAudioTrigger,
    MidiAudioTriggerResult,
    MidiAudioTriggerSettings,
    MidiInputReceiveResult,
    MidiInputReceiveSettings,
    MidiDeviceScanner,
    MidiDeviceScanResult,
    MidiDeviceSelection,
    MidiDeviceSelector,
    MidiPitchBendMapper,
    MidiMessageNormalizer,
    MidiMessage,
    MidiToNoteEventMapper,
    MidoMidiInputBackend,
    MidoStreamingVirtualMidiInputBackend,
    MidoVirtualMidiInputBackend,
    MidoVirtualMidiPortBackend,
    StreamingMidiAudioTrigger,
    StreamingMidiAudioTriggerResult,
    StreamingMidiAudioTriggerSettings,
    StreamingVoiceMode,
    UsbMidiHardwareInputAdapter,
    UsbMidiInputDiagnostic,
    VirtualMidiAudioTrigger,
    VirtualMidiAudioTriggerResult,
    VirtualMidiAudioTriggerSettings,
    VirtualMidiInputAdapter,
    VirtualMidiInputDiagnostic,
    VirtualMidiInputSettings,
    VirtualMidiPortManager,
    VirtualMidiPortResult,
    VirtualMidiPortSettings,
)
from synth.notes import Note, NoteEvent, NoteParser, NoteSequence
from synth.oscillators import Oscillator, OscillatorSettings, Waveform
from synth.wav_writer import WavWriter, WavWriteSettings


class TestCodeTraceability:
    def test_us013_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-004 Realtime CLI Playback",
            "US-013 Channel Selection",
            "Version: 0.1.0",
        )
        traceable_objects = (OutputChannel, ChannelRouter, SynthCli)

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us009_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-003 Oscillator En Audio Rendering",
            "US-009 Square Oscillator",
            "Version: 0.1.0",
        )
        traceable_objects = (Waveform, OscillatorSettings, Oscillator)

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us010_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-003 Oscillator En Audio Rendering",
            "US-010 WAV Export",
            "Version: 0.1.0",
        )
        traceable_objects = (WavWriteSettings, WavWriter)

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us020_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-020 Virtual MIDI Input Voor DAW",
            "Version: 0.1.0",
        )
        traceable_objects = (
            MidiMessage,
            VirtualMidiInputSettings,
            VirtualMidiInputDiagnostic,
            VirtualMidiInputAdapter,
            SynthCli,
        )

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us022_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-022 USB MIDI Hardware Input",
            "Version: 0.1.0",
        )
        traceable_objects = (MidiDeviceScanResult, MidiDeviceScanner, UsbMidiInputDiagnostic, UsbMidiHardwareInputAdapter, SynthCli)

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us024_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-024 MIDI Naar NoteEvent Mapping",
            "Version: 0.1.0",
        )
        traceable_objects = (MidiToNoteEventMapper,)

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us025_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-025 MIDI Device Discovery En Default Selection",
            "Version: 0.1.0",
        )
        traceable_objects = (MidiDeviceSelection, MidiDeviceSelector, SynthCli)

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us026_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-026 Live MIDI Input Receive Loop",
            "Version: 0.1.0",
        )
        traceable_objects = (
            MidiInputReceiveSettings,
            MidiInputReceiveResult,
            MidiMessageNormalizer,
            MidoMidiInputBackend,
            LiveMidiInputReceiver,
            SynthCli,
        )

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us027_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-027 Virtual MIDI Port Voor Logic/DAW",
            "Version: 0.1.0",
        )
        traceable_objects = (
            VirtualMidiPortSettings,
            VirtualMidiPortResult,
            MidoVirtualMidiPortBackend,
            VirtualMidiPortManager,
            SynthCli,
        )

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us028_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-028 External MIDI Audio Trigger Integratie",
            "Version: 0.1.0",
        )
        traceable_objects = (
            MidiAudioTriggerSettings,
            MidiAudioTriggerResult,
            MidiAudioTrigger,
            SynthCli,
        )

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us029_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-029 Logic/DAW Virtual MIDI Naar Audio Trigger",
            "Version: 0.1.0",
        )
        traceable_objects = (
            VirtualMidiAudioTriggerSettings,
            VirtualMidiAudioTriggerResult,
            MidoVirtualMidiInputBackend,
            VirtualMidiAudioTrigger,
            SynthCli,
        )

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us030_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-030 Logic MIDI Region Multi-Note Playback",
            "Version: 0.1.0",
        )
        traceable_objects = (
            MidiMessageNormalizer,
            MidoVirtualMidiInputBackend,
            VirtualMidiAudioTriggerResult,
            VirtualMidiAudioTrigger,
            SynthCli,
        )

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us031_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-031 Live/Streaming MIDI Playback Loop",
            "Version: 0.1.0",
        )
        traceable_objects = (
            StreamingMidiAudioTriggerSettings,
            StreamingMidiAudioTriggerResult,
            MidoStreamingVirtualMidiInputBackend,
            StreamingMidiAudioTrigger,
            SynthCli,
        )

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us032_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-032 Duplicate MIDI Event Guard",
            "Version: 0.1.0",
        )
        traceable_objects = (
            DuplicateMidiEventGuardSettings,
            DuplicateMidiEventGuard,
            StreamingMidiAudioTriggerSettings,
            StreamingMidiAudioTriggerResult,
            StreamingMidiAudioTrigger,
            SynthCli,
        )

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us033_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-033 Note Off Gated Voice Duration",
            "Version: 0.1.0",
        )
        traceable_objects = (
            StreamingVoiceMode,
            StreamingMidiAudioTriggerSettings,
            StreamingMidiAudioTriggerResult,
            StreamingMidiAudioTrigger,
            SynthCli,
        )

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us034_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-034 Polyphonic Voice Mixer En Triads",
            "Version: 0.1.0",
        )
        traceable_objects = (
            PolyphonicVoiceMixer,
            StreamingMidiAudioTriggerSettings,
            StreamingMidiAudioTriggerResult,
            MidoStreamingVirtualMidiInputBackend,
            StreamingMidiAudioTrigger,
            SynthCli,
        )

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us035_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-035 Sustained Note Audio Engine",
            "Version: 0.1.0",
        )
        traceable_objects = (
            SustainedAudioPlayerSettings,
            SustainedVoiceState,
            SoundDeviceSustainedAudioPlayer,
            StreamingVoiceMode,
            StreamingMidiAudioTriggerSettings,
            StreamingMidiAudioTriggerResult,
            StreamingMidiAudioTrigger,
            SynthCli,
        )

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us036_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-007 Future MIDI En DAW Integratie",
            "US-036 MIDI Pitch Bend Mapping En DSP",
            "Version: 0.1.0",
        )
        traceable_objects = (
            MidiMessage,
            MidiMessageNormalizer,
            MidiPitchBendMapper,
            SustainedVoiceState,
            SoundDeviceSustainedAudioPlayer,
            StreamingVoiceMode,
            StreamingMidiAudioTriggerSettings,
            StreamingMidiAudioTriggerResult,
            StreamingMidiAudioTrigger,
            SynthCli,
        )

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us008_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-003 Oscillator En Audio Rendering",
            "US-008 Saw Oscillator",
            "Version: 0.1.0",
        )
        traceable_objects = (Waveform, OscillatorSettings, Oscillator)

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us006_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-002 Muzikale Basisdata",
            "US-006 NoteEvent En NoteSequence Model",
            "Version: 0.1.0",
        )
        traceable_objects = (Note, NoteEvent, NoteSequence, NoteParser)

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc

    def test_us016_code_contains_required_traceability_fields(self) -> None:
        required = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprint 1 Kanban Backlog",
            "EPIC-005 Configuratie En CLI",
            "US-016 Debuglevel",
            "Version: 0.1.0",
        )
        traceable_objects = (DebugLevel, DebugReporter, SynthCli)

        for traceable_object in traceable_objects:
            doc = traceable_object.__doc__ or ""
            for expected in required:
                assert expected in doc
