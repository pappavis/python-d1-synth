# Bestand: test_cli.py
# Versienummer: 0.1.0
# Doel: CLI tests voor audio, playback, MIDI diagnostics, device selectie en virtual MIDI port workflows.
# Sprint: Future MIDI/DAW
# User-Story: US-027 Virtual MIDI Port Voor Logic/DAW
# Actie: US-027-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-027

import numpy as np

from synth.audio import AudioDevice
import synth.cli
from synth.cli import SynthCli
from synth.midi import MidiDevice, MidiInputReceiveResult, MidiMessage, VirtualMidiPortResult
from synth.notes import NoteEvent, NoteParser, NoteSequence


class TestSynthCli:
    def test_audio_list_devices_prints_output_devices(self, monkeypatch, capsys) -> None:
        class FakeScanner:
            def scan(self):
                return type(
                    "FakeScanResult",
                    (),
                    {
                        "devices": (
                            AudioDevice(
                                identifier="1",
                                name="Mac Speakers",
                                host_api="Core Audio",
                                max_input_channels=0,
                                max_output_channels=2,
                                default_sample_rate=44100.0,
                            ),
                        ),
                        "error_message": None,
                    },
                )()

        monkeypatch.setattr(synth.cli, "AudioDeviceScanner", FakeScanner)

        exit_code = SynthCli().run(["audio", "list-devices"])

        assert exit_code == 0
        assert "Mac Speakers" in capsys.readouterr().out

    def test_play_passes_audio_device_to_player(self, monkeypatch) -> None:
        calls = []

        class FakePlayer:
            def play(self, buffer, device=None):
                calls.append((buffer.samples.shape, device))

        monkeypatch.setattr(synth.cli, "SoundDeviceAudioPlayer", FakePlayer)

        exit_code = SynthCli().run(["play", "--note", "C3", "--duration", "0.01", "--audio-device", "2"])

        assert exit_code == 0
        assert calls == [((441, 2), 2)]

    def test_play_testsequence_renders_one_audio_buffer(self, monkeypatch, capsys) -> None:
        calls = []

        class FakePlayer:
            def play(self, buffer, device=None):
                calls.append((buffer.samples.shape, buffer.sample_rate, device))

        monkeypatch.setattr(synth.cli, "SoundDeviceAudioPlayer", FakePlayer)

        exit_code = SynthCli().run(
            [
                "play",
                "--testsequence",
                "ACGD",
                "--duration",
                "0.25",
                "--debuglevel",
                "verbose",
                "--audio-device",
                "Scarlett 8i6 USB",
            ]
        )

        output = capsys.readouterr().out
        assert exit_code == 0
        assert calls == [((44100, 2), 44100, "Scarlett 8i6 USB")]
        assert "Playing testsequence ACGD" in output
        assert "Sequence events: A3@0.000s, C4@0.250s, G3@0.500s, D4@0.750s" in output
        assert "Audio buffer: 44100 frames, 44100 Hz" in output

    def test_play_honors_right_channel_option(self, monkeypatch, capsys) -> None:
        calls = []

        class FakePlayer:
            def play(self, buffer, device=None):
                calls.append(buffer.samples.copy())

        monkeypatch.setattr(synth.cli, "SoundDeviceAudioPlayer", FakePlayer)

        exit_code = SynthCli().run(
            ["play", "--note", "C3", "--duration", "0.1", "--channel", "right", "--debuglevel", "verbose"]
        )

        assert exit_code == 0
        assert np.allclose(calls[0][:, 0], 0.0)
        assert np.any(np.abs(calls[0][:, 1]) > 0.0)
        assert "Output channel: right" in capsys.readouterr().out

    def test_play_debuglevel_none_suppresses_status_output(self, monkeypatch, capsys) -> None:
        class FakePlayer:
            def play(self, buffer, device=None):
                return None

        monkeypatch.setattr(synth.cli, "SoundDeviceAudioPlayer", FakePlayer)

        exit_code = SynthCli().run(["play", "--note", "C3", "--duration", "0.01", "--debuglevel", "none"])

        assert exit_code == 0
        assert capsys.readouterr().out == ""

    def test_play_debuglevel_light_outputs_main_action_only(self, monkeypatch, capsys) -> None:
        class FakePlayer:
            def play(self, buffer, device=None):
                return None

        monkeypatch.setattr(synth.cli, "SoundDeviceAudioPlayer", FakePlayer)

        exit_code = SynthCli().run(["play", "--note", "C3", "--duration", "0.01", "--debuglevel", "light"])

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "Playing note C3" in output
        assert "Playback settings:" not in output
        assert "Audio buffer:" not in output

    def test_play_debuglevel_verbose_outputs_technical_details(self, monkeypatch, capsys) -> None:
        class FakePlayer:
            def play(self, buffer, device=None):
                return None

        monkeypatch.setattr(synth.cli, "SoundDeviceAudioPlayer", FakePlayer)

        exit_code = SynthCli().run(["play", "--note", "C3", "--duration", "0.01", "--debuglevel", "verbose"])

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "Playing note C3" in output
        assert "Playback settings: waveform=sine, duration=0.01s, sample_rate=44100 Hz, channel=stereo" in output
        assert "Audio buffer: 441 frames, 44100 Hz" in output

    def test_midi_diagnose_virtual_input_reports_backend_status(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(synth.cli.importlib.util, "find_spec", lambda name: None)

        exit_code = SynthCli().run(["midi", "diagnose-virtual-input"])

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "Virtual MIDI input backend is not available" in output

    def test_midi_virtual_port_opens_selected_port_with_bounded_timeout(self, monkeypatch, capsys) -> None:
        class FakeVirtualMidiPortManager:
            def open(self, settings):
                assert settings.port_name == "python-d1-synth"
                assert settings.timeout_seconds == 0.5
                return VirtualMidiPortResult(
                    port_name=settings.port_name,
                    opened=True,
                    message="Virtual MIDI input port opened: python-d1-synth.",
                )

        monkeypatch.setattr(synth.cli, "VirtualMidiPortManager", FakeVirtualMidiPortManager)

        exit_code = SynthCli().run(
            [
                "midi",
                "virtual-port",
                "--name",
                "python-d1-synth",
                "--timeout",
                "0.5",
                "--debuglevel",
                "light",
            ]
        )

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "Opening virtual MIDI input port: python-d1-synth" in output
        assert "Virtual MIDI input port opened: python-d1-synth." in output

    def test_midi_virtual_port_reports_backend_error(self, monkeypatch, capsys) -> None:
        class FakeVirtualMidiPortManager:
            def open(self, settings):
                raise RuntimeError("Virtual MIDI port could not be opened.")

        monkeypatch.setattr(synth.cli, "VirtualMidiPortManager", FakeVirtualMidiPortManager)

        exit_code = SynthCli().run(["midi", "virtual-port", "--name", "python-d1-synth", "--timeout", "0.5"])

        captured = capsys.readouterr()
        assert exit_code == 2
        assert "Virtual MIDI port error: Virtual MIDI port could not be opened." in captured.err

    def test_midi_virtual_port_reports_invalid_settings_without_traceback(self, capsys) -> None:
        exit_code = SynthCli().run(["midi", "virtual-port", "--name", "python-d1-synth", "--timeout", "0"])

        captured = capsys.readouterr()
        assert exit_code == 2
        assert "Virtual MIDI port error: timeout_seconds must be positive" in captured.err

    def test_midi_diagnose_usb_input_accepts_generic_input_device(self, monkeypatch, capsys) -> None:
        class FakeScanner:
            def __init__(self, allow_unsafe_native_scan=False):
                self.allow_unsafe_native_scan = allow_unsafe_native_scan

            def scan(self):
                return type(
                    "FakeMidiScanResult",
                    (),
                    {
                        "devices": (
                            MidiDevice(identifier="input:0", name="Fishman TriplePlay", direction="input"),
                            MidiDevice(identifier="input:1", name="M-Vave MIDI", direction="input"),
                        ),
                        "error_message": None,
                    },
                )()

        monkeypatch.setattr(synth.cli, "MidiDeviceScanner", FakeScanner)

        exit_code = SynthCli().run(["midi", "diagnose-usb-input", "--midi-device", "Fishman"])

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "USB MIDI input ready: Fishman TriplePlay" in output

    def test_midi_diagnose_usb_input_guides_user_when_backend_scan_fails(self, monkeypatch, capsys) -> None:
        class FakeScanner:
            def __init__(self, allow_unsafe_native_scan=False):
                self.allow_unsafe_native_scan = allow_unsafe_native_scan

            def scan(self):
                return type(
                    "FakeMidiScanResult",
                    (),
                    {
                        "devices": tuple(),
                        "error_message": "MIDI backend failed while scanning devices.",
                    },
                )()

        monkeypatch.setattr(synth.cli, "MidiDeviceScanner", FakeScanner)

        exit_code = SynthCli().run(["midi", "diagnose-usb-input", "--midi-device", "Fishman"])

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "MIDI backend failed while scanning devices." in output
        assert "First run: python -m synth midi list-devices --unsafe-rtmidi-scan" in output
        assert "If Logic Pro shows devices but Python does not" in output

    def test_midi_list_devices_guides_user_when_backend_scan_fails(self, monkeypatch, capsys) -> None:
        class FakeScanner:
            def __init__(self, allow_unsafe_native_scan=False):
                self.allow_unsafe_native_scan = allow_unsafe_native_scan

            def scan(self):
                return type(
                    "FakeMidiScanResult",
                    (),
                    {
                        "devices": tuple(),
                        "error_message": "MIDI backend failed while scanning devices.",
                        "backend_name": "mido/python-rtmidi",
                        "returncode": -6,
                        "stderr": "CoreMIDI client init failed",
                        "stdout": "",
                    },
                )()

        monkeypatch.setattr(synth.cli, "MidiDeviceScanner", FakeScanner)

        exit_code = SynthCli().run(["midi", "list-devices", "--unsafe-rtmidi-scan", "--debuglevel", "light"])

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "MIDI backend failed while scanning devices." in output
        assert "If Logic Pro shows devices but Python does not" in output

    def test_midi_list_devices_marks_logic_visible_scan_failure_as_blocker(self, monkeypatch, capsys) -> None:
        class FakeScanner:
            def __init__(self, allow_unsafe_native_scan=False):
                self.allow_unsafe_native_scan = allow_unsafe_native_scan

            def scan(self):
                return type(
                    "FakeMidiScanResult",
                    (),
                    {
                        "devices": tuple(),
                        "error_message": "MIDI backend failed while scanning devices.",
                        "backend_name": "mido/python-rtmidi",
                        "returncode": -6,
                        "stderr": "MidiInCore::initialize: error creating OS-X MIDI client object (-10833)",
                        "stdout": "",
                    },
                )()

        monkeypatch.setattr(synth.cli, "MidiDeviceScanner", FakeScanner)

        exit_code = SynthCli().run(["midi", "list-devices", "--unsafe-rtmidi-scan", "--debuglevel", "light"])

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "MIDI backend: mido/python-rtmidi" in output
        assert "MIDI backend return code: -6" in output
        assert "MIDI backend stderr: MidiInCore::initialize" in output
        assert "BLOCKER: Logic Pro shows MIDI devices but Python scan returned none." in output

    def test_midi_list_devices_summarizes_traceback_with_last_error_line(self, monkeypatch, capsys) -> None:
        class FakeScanner:
            def __init__(self, allow_unsafe_native_scan=False):
                self.allow_unsafe_native_scan = allow_unsafe_native_scan

            def scan(self):
                return type(
                    "FakeMidiScanResult",
                    (),
                    {
                        "devices": tuple(),
                        "error_message": "MIDI backend failed while scanning devices.",
                        "backend_name": "mido/python-rtmidi",
                        "returncode": 1,
                        "stderr": "Traceback (most recent call last):\nModuleNotFoundError: No module named 'mido'",
                        "stdout": "",
                    },
                )()

        monkeypatch.setattr(synth.cli, "MidiDeviceScanner", FakeScanner)

        exit_code = SynthCli().run(["midi", "list-devices", "--unsafe-rtmidi-scan", "--debuglevel", "light"])

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "MIDI backend stderr: ModuleNotFoundError: No module named 'mido'" in output

    def test_midi_list_devices_selects_device_by_identifier(self, monkeypatch, capsys) -> None:
        class FakeScanner:
            def __init__(self, allow_unsafe_native_scan=False):
                self.allow_unsafe_native_scan = allow_unsafe_native_scan

            def scan(self):
                return type(
                    "FakeMidiScanResult",
                    (),
                    {
                        "devices": (
                            MidiDevice(identifier="input:0", name="Generic Keyboard", direction="input"),
                            MidiDevice(identifier="input:1", name="Generic Guitar MIDI", direction="input"),
                            MidiDevice(identifier="output:0", name="Generic Synth", direction="output"),
                        ),
                        "error_message": None,
                    },
                )()

        monkeypatch.setattr(synth.cli, "MidiDeviceScanner", FakeScanner)

        exit_code = SynthCli().run(
            ["midi", "list-devices", "--midi-device-id", "input:1", "--debuglevel", "light"]
        )

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "input:1\tinput\tGeneric Guitar MIDI" in output
        assert "Selected MIDI input device from cli-id: input:1 Generic Guitar MIDI" in output

    def test_midi_list_devices_uses_config_default_without_cli_override(self, monkeypatch, capsys, tmp_path) -> None:
        config = tmp_path / "patch.yaml"
        config.write_text(
            "\n".join(
                [
                    "midi:",
                    "  default_input_device: Generic Keyboard",
                ]
            ),
            encoding="utf-8",
        )

        class FakeScanner:
            def __init__(self, allow_unsafe_native_scan=False):
                self.allow_unsafe_native_scan = allow_unsafe_native_scan

            def scan(self):
                return type(
                    "FakeMidiScanResult",
                    (),
                    {
                        "devices": (
                            MidiDevice(identifier="input:0", name="Generic Keyboard", direction="input"),
                            MidiDevice(identifier="input:1", name="Generic Guitar MIDI", direction="input"),
                        ),
                        "error_message": None,
                    },
                )()

        monkeypatch.setattr(synth.cli, "MidiDeviceScanner", FakeScanner)

        exit_code = SynthCli().run(["midi", "list-devices", "--config", str(config), "--debuglevel", "light"])

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "Selected MIDI input device from config: input:0 Generic Keyboard" in output

    def test_midi_list_devices_cli_device_wins_over_config_default(self, monkeypatch, capsys, tmp_path) -> None:
        config = tmp_path / "patch.yaml"
        config.write_text(
            "\n".join(
                [
                    "midi:",
                    "  default_input_device: Generic Keyboard",
                ]
            ),
            encoding="utf-8",
        )

        class FakeScanner:
            def __init__(self, allow_unsafe_native_scan=False):
                self.allow_unsafe_native_scan = allow_unsafe_native_scan

            def scan(self):
                return type(
                    "FakeMidiScanResult",
                    (),
                    {
                        "devices": (
                            MidiDevice(identifier="input:0", name="Generic Keyboard", direction="input"),
                            MidiDevice(identifier="input:1", name="Generic Guitar MIDI", direction="input"),
                        ),
                        "error_message": None,
                    },
                )()

        monkeypatch.setattr(synth.cli, "MidiDeviceScanner", FakeScanner)

        exit_code = SynthCli().run(
            [
                "midi",
                "list-devices",
                "--config",
                str(config),
                "--midi-device",
                "Guitar",
                "--debuglevel",
                "light",
            ]
        )

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "Selected MIDI input device from cli: input:1 Generic Guitar MIDI" in output

    def test_midi_list_devices_reports_missing_selected_input(self, monkeypatch, capsys) -> None:
        class FakeScanner:
            def __init__(self, allow_unsafe_native_scan=False):
                self.allow_unsafe_native_scan = allow_unsafe_native_scan

            def scan(self):
                return type(
                    "FakeMidiScanResult",
                    (),
                    {
                        "devices": (MidiDevice(identifier="input:0", name="Generic Keyboard", direction="input"),),
                        "error_message": None,
                    },
                )()

        monkeypatch.setattr(synth.cli, "MidiDeviceScanner", FakeScanner)

        exit_code = SynthCli().run(["midi", "list-devices", "--midi-device", "Missing", "--debuglevel", "light"])

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "Requested MIDI input device not found" in output
        assert "Available input devices: input:0 Generic Keyboard" in output

    def test_midi_listen_receives_messages_from_selected_input(self, monkeypatch, capsys) -> None:
        class FakeScanner:
            def __init__(self, allow_unsafe_native_scan=False):
                self.allow_unsafe_native_scan = allow_unsafe_native_scan

            def scan(self):
                return type(
                    "FakeMidiScanResult",
                    (),
                    {
                        "devices": (MidiDevice(identifier="input:0", name="Generic Keyboard", direction="input"),),
                        "error_message": None,
                    },
                )()

        class FakeReceiver:
            def receive(self, settings):
                assert settings.input_name == "Generic Keyboard"
                assert settings.max_messages == 2
                assert settings.timeout_seconds == 0.5
                note = NoteParser().parse("C4")
                return MidiInputReceiveResult(
                    input_name=settings.input_name,
                    received_messages=(
                        MidiMessage(message_type="note_on", note_number=60, velocity=90, channel=1, time_seconds=0.0),
                        MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.25),
                    ),
                    note_sequence=NoteSequence(
                        events=(NoteEvent(note=note, duration_seconds=0.25, velocity=90 / 127),)
                    ),
                    message="Received 2 MIDI note messages from Generic Keyboard.",
                )

        monkeypatch.setattr(synth.cli, "MidiDeviceScanner", FakeScanner)
        monkeypatch.setattr(synth.cli, "LiveMidiInputReceiver", FakeReceiver)

        exit_code = SynthCli().run(
            [
                "midi",
                "listen",
                "--midi-device",
                "Generic",
                "--max-messages",
                "2",
                "--timeout",
                "0.5",
                "--debuglevel",
                "light",
            ]
        )

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "Selected MIDI input device from cli: input:0 Generic Keyboard" in output
        assert "Received 2 MIDI note messages from Generic Keyboard." in output
        assert "Received sequence: C4@0.000s" in output
