# Bestand: test_docs.py
# Versienummer: 0.1.0
# Doel: Controleert dat story-documentatie traceerbare verplichte termen bevat.
# Sprint: Future MIDI/DAW
# User-Story: US-028 External MIDI Audio Trigger Integratie
# Actie: US-028-DOCS-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-028

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

    def test_us023_studio_midi_routing_doc_contains_required_terms(self) -> None:
        document = Path("docs/studio_midi_routing_integration_v0.1.0.md")

        content = document.read_text(encoding="utf-8")

        required_terms = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprintnummer: Future MIDI/DAW",
            "Doc versie: 0.1.0",
            "US-023 Studio MIDI Routing Integratietest",
            "EPIC-007 Future MIDI En DAW Integratie",
            "Status: Done",
            "Routing Matrix Template",
            "KodeklopperM4 Snapshot",
            "MuziekM4 Snapshot",
            "Spelen01",
            "Raspberry Pi 2",
            "placeholders",
            "constants",
            "runtime MIDI device discovery",
            "Muziekm4_midi_devices_scanned_2026-07-10.txt",
            "GM-800",
            "TriplePlay Express Geel strat TP Guitar",
            "KL Essential 49 mk3 MIDI",
            "SN76489 Synth Pappavis CircuitPython usb_midi.ports[0]",
            "CircuitPython/ESP32",
        )
        for term in required_terms:
            assert term in content

    def test_us024_midi_to_note_event_mapping_doc_contains_required_terms(self) -> None:
        document = Path("docs/midi_to_note_event_mapping_v0.1.0.md")

        content = document.read_text(encoding="utf-8")

        required_terms = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprintnummer: Future MIDI/DAW",
            "Doc versie: 0.1.0",
            "US-024 MIDI Naar NoteEvent Mapping",
            "EPIC-007 Future MIDI En DAW Integratie",
            "Status: Done",
            "MidiToNoteEventMapper",
            "MidiMessage",
            "NoteEvent",
            "NoteSequence",
            "note_on",
            "note_off",
            "velocity 0",
            "channel",
            "default duration",
            "C4",
            "MIDI note number 60",
            "geen hardcoded MIDI device names",
        )
        for term in required_terms:
            assert term in content

    def test_us025_midi_device_discovery_default_selection_doc_contains_required_terms(self) -> None:
        document = Path("docs/midi_device_discovery_default_selection_v0.1.0.md")

        content = document.read_text(encoding="utf-8")

        required_terms = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprintnummer: Future MIDI/DAW",
            "Doc versie: 0.1.0",
            "US-025 MIDI Device Discovery En Default Selection",
            "EPIC-007 Future MIDI En DAW Integratie",
            "Status: Done",
            "MidiDeviceScanner",
            "MidiDeviceSelector",
            "MidiDeviceSelection",
            "--midi-device",
            "--midi-device-id",
            "--config",
            "midi.default_input_device",
            "CLI wint van YAML",
            "--unsafe-rtmidi-scan",
            "geen hardcoded MIDI device names",
            "KodeklopperM4",
            "MuziekM4",
            "Spelen01",
            "Raspberry Pi 2",
        )
        for term in required_terms:
            assert term in content

    def test_us026_live_midi_input_receive_loop_doc_contains_required_terms(self) -> None:
        document = Path("docs/live_midi_input_receive_loop_v0.1.0.md")

        content = document.read_text(encoding="utf-8")

        required_terms = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprintnummer: Future MIDI/DAW",
            "Doc versie: 0.1.0",
            "US-026 Live MIDI Input Receive Loop",
            "EPIC-007 Future MIDI En DAW Integratie",
            "Status: Done",
            "midi listen",
            "LiveMidiInputReceiver",
            "MidiInputReceiveSettings",
            "MidiInputReceiveResult",
            "MidiMessageNormalizer",
            "MidoMidiInputBackend",
            "MidiMessage",
            "NoteSequence",
            "fake backend",
            "geen Logic virtual device",
            "geen realtime audio-trigger",
            "hardwaretest pauzeert bij klant",
            "MidiportA",
            "SMK 37 Pro BLE",
            "geen hardcoded MIDI device names",
            "US-026-HARDWARE-TESTRESULT",
            "Host: KodeklopperM4",
            "Status: Geslaagd",
            "SMK-37 Pro_BLE Bluetooth",
            "Selected MIDI input device from cli: input:7 SMK-37 Pro_BLE Bluetooth",
            "Received 10 MIDI note messages from SMK-37 Pro_BLE Bluetooth.",
            "Selected MIDI input device from cli-id: input:7 SMK-37 Pro_BLE Bluetooth",
            "Received 4 MIDI note messages from SMK-37 Pro_BLE Bluetooth.",
            "input:9 input   Logic Pro Virtual Out",
            "output:10       output  Logic Pro Virtual In",
            "hardwarematig geslaagd op KodeklopperM4",
        )
        for term in required_terms:
            assert term in content

    def test_us027_virtual_midi_port_logic_daw_doc_contains_required_terms(self) -> None:
        document = Path("docs/virtual_midi_port_logic_daw_v0.1.0.md")

        content = document.read_text(encoding="utf-8")

        required_terms = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprintnummer: Future MIDI/DAW",
            "Doc versie: 0.1.0",
            "US-027 Virtual MIDI Port Voor Logic/DAW",
            "EPIC-007 Future MIDI En DAW Integratie",
            "Status: Done",
            "midi virtual-port",
            "python-d1-synth",
            "Logic Pro 12.3",
            "virtual MIDI destination",
            "VirtualMidiPortSettings",
            "VirtualMidiPortResult",
            "MidoVirtualMidiPortBackend",
            "VirtualMidiPortManager",
            "fake backend",
            "geen realtime audio-trigger",
            "US-028",
            "hardware/Logic test pauzeert bij klant",
            "geen hardcoded MIDI device names",
            "US-027-IN-REVIEW",
            "2026-07-10 19:25",
            "External MIDI",
            "MIDI destination",
            "Software Instrument",
            "virtual instrument",
            "verwacht en geen US-027 defect",
            "geslaagd is",
        )
        for term in required_terms:
            assert term in content

    def test_us028_external_midi_audio_trigger_doc_contains_required_terms(self) -> None:
        document = Path("docs/external_midi_audio_trigger_v0.1.0.md")

        content = document.read_text(encoding="utf-8")

        required_terms = (
            "CHATOD-20260709-D1PY-MVP-001",
            "Sprintnummer: Future MIDI/DAW",
            "Doc versie: 0.1.0",
            "US-028 External MIDI Audio Trigger Integratie",
            "EPIC-007 Future MIDI En DAW Integratie",
            "Status: In Review",
            "midi play-live",
            "MidiAudioTriggerSettings",
            "MidiAudioTriggerResult",
            "MidiAudioTrigger",
            "LiveMidiInputReceiver",
            "SynthEngine",
            "SoundDeviceAudioPlayer",
            "fake MIDI backend",
            "fake audio player",
            "bounded",
            "geen GUI",
            "geen plugin",
            "geen onbeperkte realtime performance-loop",
            "hardwaretest pauzeert bij klant",
            "geen hardcoded MIDI device names",
            "Scarlett 8i6 USB",
            "SMK-37 Pro_BLE",
            "US-028-HARDWARE-TEST",
        )
        for term in required_terms:
            assert term in content
