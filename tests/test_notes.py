import pytest

from synth.notes import NoteParser


class TestNoteParser:
    def test_parse_a4_is_440_hz(self) -> None:
        note = NoteParser().parse("A4")

        assert note.frequency_hz == pytest.approx(440.0)

    def test_parse_c3_is_expected_frequency(self) -> None:
        note = NoteParser().parse("C3")

        assert note.frequency_hz == pytest.approx(130.81, abs=0.01)

    def test_testsequence_default_octaves(self) -> None:
        sequence = NoteParser().parse_testsequence("ACGD", duration_seconds=0.25)

        assert [f"{event.note.name}{event.note.octave}" for event in sequence.events] == ["A3", "C4", "G3", "D4"]

