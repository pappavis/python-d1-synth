from synth.audio import ChannelRouter, OutputChannel
from synth.cli import SynthCli


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
