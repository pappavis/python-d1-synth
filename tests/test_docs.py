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
            "2026-07-10 14:28",
            "MIDI backend failed while scanning devices.",
            "Status: Done",
            "BLOCKER: Logic Pro shows MIDI devices but Python scan returned none.",
            "tests/test_hardware_midi.py",
            "PYTHON_D1_RUN_HARDWARE_MIDI=1",
            "US-022-CRASHLOGS",
            "35DB83DC-374A-4C19-80DE-8D43E29AF27A",
            "FEE3C08D-0AB5-492E-BF4A-AC399EA64D14",
            "MidiInCore::initialize",
            "EXC_CRASH (SIGABRT)",
            "US-022-SUCCESS-TESTRESULT",
            "2026-07-10 18:01:41",
            "input:8 input   SN76489 Synth Pappavis CircuitPython usb_midi.ports[0]",
            "output:9        output  Software Synthesizer",
            "Lolin Wemos ESP32 S2",
            "CircuitPython 10",
            "US-022 status: `Done`",
        )
        for term in required_terms:
            assert term in content
