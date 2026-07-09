from synth.audio import ChannelRouter, OutputChannel
from synth.cli import SynthCli
from synth.debug import DebugLevel, DebugReporter
from synth.notes import Note, NoteEvent, NoteParser, NoteSequence


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
