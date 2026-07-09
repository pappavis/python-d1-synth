from pathlib import Path


class TestDocumentationArtifacts:
    def test_us019_midi_learning_path_contains_required_terms(self) -> None:
        document = Path("docs/midi_learning_path_v0.1.0.md")

        content = document.read_text(encoding="utf-8")

        required_terms = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprintnummer: Future MIDI/DAW",
            "Doc versie: 0.1.0",
            "US-019 MIDI Leerpad En Terminologie",
            "note on",
            "note off",
            "note number",
            "velocity",
            "channel",
            "MIDI clock",
            "pitch bend",
            "NoteEvent",
            "Arturia KeyLab Mk3",
            "Logic Pro 12.3",
        )
        for term in required_terms:
            assert term in content

    def test_us020_virtual_midi_input_doc_contains_required_terms(self) -> None:
        document = Path("docs/virtual_midi_input_v0.1.0.md")

        content = document.read_text(encoding="utf-8")

        required_terms = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprintnummer: Future MIDI/DAW",
            "Doc versie: 0.1.0",
            "US-020 Virtual MIDI Input Voor DAW",
            "Logic Pro 12.3",
            "MidiMessage",
            "VirtualMidiInputAdapter",
            "note_on",
            "note_off",
            "NoteSequence",
            "NoteEvent",
            "midi diagnose-virtual-input",
        )
        for term in required_terms:
            assert term in content
