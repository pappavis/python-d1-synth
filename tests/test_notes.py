import pytest

from synth.notes import NoteEvent, NoteParser, NoteSequence


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


class TestNoteEvent:
    def test_validates_duration_velocity_and_start_time(self) -> None:
        note = NoteParser().parse("C3")

        event = NoteEvent(note=note, duration_seconds=0.5, velocity=0.75, start_seconds=0.25)

        assert event.note is note
        assert event.duration_seconds == 0.5
        assert event.velocity == 0.75
        assert event.start_seconds == 0.25

    def test_rejects_invalid_duration_velocity_and_start_time(self) -> None:
        note = NoteParser().parse("C3")

        with pytest.raises(ValueError, match="duration_seconds"):
            NoteEvent(note=note, duration_seconds=0.0, velocity=1.0)
        with pytest.raises(ValueError, match="velocity"):
            NoteEvent(note=note, duration_seconds=0.5, velocity=1.1)
        with pytest.raises(ValueError, match="start_seconds"):
            NoteEvent(note=note, duration_seconds=0.5, velocity=1.0, start_seconds=-0.1)


class TestNoteSequence:
    def test_preserves_order_and_total_duration(self) -> None:
        parser = NoteParser()
        first = NoteEvent(note=parser.parse("C3"), duration_seconds=0.5, velocity=1.0, start_seconds=0.0)
        second = NoteEvent(note=parser.parse("D3"), duration_seconds=0.25, velocity=0.5, start_seconds=0.5)

        sequence = NoteSequence(events=[first, second])

        assert sequence.events == (first, second)
        assert sequence.total_duration_seconds() == 0.75

    def test_rejects_non_note_events(self) -> None:
        with pytest.raises(ValueError, match="events must contain NoteEvent instances"):
            NoteSequence(events=("not-a-note-event",))
