from synth.audio import ChannelRouter, OutputChannel
from synth.cli import SynthCli
from synth.debug import DebugLevel, DebugReporter
from synth.midi import MidiMessage, VirtualMidiInputAdapter, VirtualMidiInputDiagnostic, VirtualMidiInputSettings
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
