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

    def test_us021_logic_external_midi_workflow_doc_contains_required_terms(self) -> None:
        document = Path("docs/logic_external_midi_workflow_v0.1.0.md")

        content = document.read_text(encoding="utf-8")

        required_terms = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprintnummer: Future MIDI/DAW",
            "Doc versie: 0.1.0",
            "US-021 External MIDI Workflow In Logic",
            "Logic Pro 12.3",
            "IAC Driver",
            "Audio MIDI Setup",
            "External MIDI",
            "python-d1-synth",
            "midi diagnose-virtual-input",
            "Handmatige test",
            "Testresultaat",
            "Beoordeling: geslaagd voor US-021",
            "geen geluid is verwacht in US-021",
        )
        for term in required_terms:
            assert term in content

    def test_us022_usb_midi_hardware_input_doc_contains_required_terms(self) -> None:
        document = Path("docs/usb_midi_hardware_input_v0.1.0.md")

        content = document.read_text(encoding="utf-8")

        required_terms = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprintnummer: Future MIDI/DAW",
            "Doc versie: 0.1.0",
            "US-022 USB MIDI Hardware Input",
            "Fishman TriplePlay",
            "M-Vave",
            "Arturia KeyLab Mk3",
            "UsbMidiHardwareInputAdapter",
            "midi diagnose-usb-input",
            "Handmatige hardwaretest",
            "Testresultaat",
            "list-devices",
            "KodeklopperM4",
            "MuziekM4",
            "default device",
            "Logic Pro shows devices but Python does not",
        )
        for term in required_terms:
            assert term in content
