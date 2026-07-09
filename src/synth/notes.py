from dataclasses import dataclass
import math
import re


@dataclass(frozen=True)
class Note:
    """Parsed musical note with calculated frequency.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-006
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-002 Muzikale Basisdata
    - User Story: US-006 NoteEvent En NoteSequence Model
    - Version: 0.1.0
    """

    name: str
    octave: int
    frequency_hz: float


@dataclass(frozen=True)
class NoteEvent:
    """Internal timed note event used by the synth engine and future MIDI mapping.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-006
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-002 Muzikale Basisdata
    - User Story: US-006 NoteEvent En NoteSequence Model
    - Version: 0.1.0
    """

    note: Note
    duration_seconds: float
    velocity: float
    start_seconds: float = 0.0

    def __post_init__(self) -> None:
        if self.duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
        if not 0.0 <= self.velocity <= 1.0:
            raise ValueError("velocity must be between 0.0 and 1.0")
        if self.start_seconds < 0:
            raise ValueError("start_seconds must not be negative")


@dataclass(frozen=True)
class NoteSequence:
    """Ordered immutable collection of note events.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-006
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-002 Muzikale Basisdata
    - User Story: US-006 NoteEvent En NoteSequence Model
    - Version: 0.1.0
    """

    events: tuple[NoteEvent, ...]

    def __post_init__(self) -> None:
        events = tuple(self.events)
        if any(not isinstance(event, NoteEvent) for event in events):
            raise ValueError("events must contain NoteEvent instances")
        object.__setattr__(self, "events", events)

    def total_duration_seconds(self) -> float:
        if not self.events:
            return 0.0
        return max(event.start_seconds + event.duration_seconds for event in self.events)


class NoteParser:
    """Parse note names and simple test sequences into the internal note model.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-006
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-002 Muzikale Basisdata
    - User Story: US-006 NoteEvent En NoteSequence Model
    - Version: 0.1.0
    """

    def parse(self, value: str) -> Note:
        match = re.fullmatch(r"([A-Ga-g])([#b]?)(-?\d+)", value.strip())
        if match is None:
            raise ValueError(f"Invalid note '{value}'. Expected format like C3 or A4.")
        letter, accidental, octave_text = match.groups()
        name = f"{letter.upper()}{accidental}"
        octave = int(octave_text)
        midi_number = self._midi_number(name, octave)
        frequency = 440.0 * math.pow(2.0, (midi_number - 69) / 12.0)
        return Note(name=name, octave=octave, frequency_hz=frequency)

    def parse_testsequence(self, value: str, duration_seconds: float) -> NoteSequence:
        cleaned = value.strip().replace(" ", "")
        if not cleaned:
            raise ValueError("testsequence must not be empty")

        events: list[NoteEvent] = []
        index = 0
        start_seconds = 0.0
        while index < len(cleaned):
            token_match = re.match(r"([A-Ga-g])([#b]?)(-?\d+)?", cleaned[index:])
            if token_match is None:
                raise ValueError(f"Invalid testsequence near '{cleaned[index:]}'")
            letter, accidental, octave_text = token_match.groups()
            octave = int(octave_text) if octave_text is not None else self._default_octave(letter)
            note = self.parse(f"{letter.upper()}{accidental}{octave}")
            events.append(NoteEvent(note=note, duration_seconds=duration_seconds, velocity=1.0, start_seconds=start_seconds))
            start_seconds += duration_seconds
            index += len(token_match.group(0))

        return NoteSequence(events=tuple(events))

    def _midi_number(self, name: str, octave: int) -> int:
        semitone_map = {
            "C": 0,
            "C#": 1,
            "Db": 1,
            "D": 2,
            "D#": 3,
            "Eb": 3,
            "E": 4,
            "F": 5,
            "F#": 6,
            "Gb": 6,
            "G": 7,
            "G#": 8,
            "Ab": 8,
            "A": 9,
            "A#": 10,
            "Bb": 10,
            "B": 11,
        }
        if name not in semitone_map:
            raise ValueError(f"Unsupported note name '{name}'")
        return (octave + 1) * 12 + semitone_map[name]

    def _default_octave(self, letter: str) -> int:
        octave_map = {
            "A": 3,
            "B": 3,
            "C": 4,
            "D": 4,
            "E": 4,
            "F": 4,
            "G": 3,
        }
        return octave_map[letter.upper()]
