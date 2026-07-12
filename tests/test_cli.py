# Bestand: test_cli.py
# Versienummer: 0.1.0
# Doel: CLI tests voor audio, playback, MIDI diagnostics, device selectie en virtual MIDI audio trigger workflows.
# Sprint: Future MIDI/DAW
# User-Story: US-040 Envelope Release / Soft Note-Off
# Actie: US-040-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-040

import numpy as np

from synth.audio import AudioDevice, AudioDeviceSelection, OutputChannel
import synth.cli
from synth.cli import SynthCli
from synth.midi import (
    MidiAudioTriggerResult,
    MidiDevice,
    MidiInputReceiveResult,
    MidiMessage,
    PitchBendChannelMode,
    StreamingMidiAudioTriggerResult,
    StreamingVoiceMode,
    VirtualMidiAudioTriggerResult,
    VirtualMidiPortResult,
)
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

    def test_midi_play_live_triggers_audio_from_selected_input(self, monkeypatch, capsys) -> None:
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

        class FakeAudioSelector:
            def select(self, cli_device):
                assert cli_device == "Scarlett 8i6 USB"
                return AudioDeviceSelection(sounddevice_value="Scarlett 8i6 USB", source="cli")

        class FakeMidiAudioTrigger:
            def trigger(self, settings):
                assert settings.input_name == "Generic Keyboard"
                assert settings.max_messages == 2
                assert settings.timeout_seconds == 0.5
                assert settings.sample_rate == 44100
                assert settings.channel is OutputChannel.STEREO
                assert settings.audio_device == "Scarlett 8i6 USB"
                return MidiAudioTriggerResult(
                    input_name=settings.input_name,
                    received_message_count=2,
                    played_event_count=1,
                    audio_frame_count=4410,
                    sample_rate=44100,
                    message="Played 1 MIDI-triggered note events from Generic Keyboard.",
                )

        monkeypatch.setattr(synth.cli, "MidiDeviceScanner", FakeScanner)
        monkeypatch.setattr(synth.cli, "AudioDeviceSelector", FakeAudioSelector)
        monkeypatch.setattr(synth.cli, "MidiAudioTrigger", FakeMidiAudioTrigger)

        exit_code = SynthCli().run(
            [
                "midi",
                "play-live",
                "--midi-device",
                "Generic",
                "--audio-device",
                "Scarlett 8i6 USB",
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
        assert "Selected audio device from cli: Scarlett 8i6 USB" in output
        assert "Played 1 MIDI-triggered note events from Generic Keyboard." in output

    def test_midi_play_virtual_triggers_audio_from_virtual_port(self, monkeypatch, capsys) -> None:
        class FakeAudioSelector:
            def select(self, cli_device):
                assert cli_device == "Scarlett 8i6 USB"
                return AudioDeviceSelection(sounddevice_value="Scarlett 8i6 USB", source="cli")

        class FakeVirtualMidiAudioTrigger:
            def trigger(self, settings):
                assert settings.port_name == "python-d1-synth"
                assert settings.max_messages == 2
                assert settings.timeout_seconds == 0.5
                assert settings.sample_rate == 44100
                assert settings.channel is OutputChannel.STEREO
                assert settings.audio_device == "Scarlett 8i6 USB"
                return VirtualMidiAudioTriggerResult(
                    port_name=settings.port_name,
                    received_message_count=2,
                    played_event_count=1,
                    audio_frame_count=4410,
                    sample_rate=44100,
                    message="Played 1 MIDI-triggered note events from virtual MIDI port python-d1-synth.",
                    received_messages=(
                        MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=0.0),
                    ),
                )

        monkeypatch.setattr(synth.cli, "AudioDeviceSelector", FakeAudioSelector)
        monkeypatch.setattr(synth.cli, "VirtualMidiAudioTrigger", FakeVirtualMidiAudioTrigger)

        exit_code = SynthCli().run(
            [
                "midi",
                "play-virtual",
                "--port-name",
                "python-d1-synth",
                "--audio-device",
                "Scarlett 8i6 USB",
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
        assert "Opening virtual MIDI input port: python-d1-synth" in output
        assert "audio is rendered after --max-messages is reached or --timeout expires" in output
        assert "Selected audio device from cli: Scarlett 8i6 USB" in output
        assert "Played 1 MIDI-triggered note events from virtual MIDI port python-d1-synth." in output

    def test_midi_play_virtual_verbose_prints_received_midi_messages(self, monkeypatch, capsys) -> None:
        class FakeAudioSelector:
            def select(self, cli_device):
                return AudioDeviceSelection(sounddevice_value=None, source="none")

        class FakeVirtualMidiAudioTrigger:
            def trigger(self, settings):
                return VirtualMidiAudioTriggerResult(
                    port_name=settings.port_name,
                    received_message_count=1,
                    played_event_count=1,
                    audio_frame_count=44100,
                    sample_rate=44100,
                    message="Played 1 MIDI-triggered note events from virtual MIDI port python-d1-synth.",
                    received_messages=(
                        MidiMessage(message_type="note_on", note_number=60, velocity=96, channel=1, time_seconds=0.0),
                    ),
                    played_events=(
                        NoteEvent(note=NoteParser().parse("C4"), duration_seconds=1.0, velocity=96 / 127),
                    ),
                )

        monkeypatch.setattr(synth.cli, "AudioDeviceSelector", FakeAudioSelector)
        monkeypatch.setattr(synth.cli, "VirtualMidiAudioTrigger", FakeVirtualMidiAudioTrigger)

        exit_code = SynthCli().run(
            [
                "midi",
                "play-virtual",
                "--port-name",
                "python-d1-synth",
                "--max-messages",
                "1",
                "--timeout",
                "10",
                "--debuglevel",
                "verbose",
            ]
        )

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "port=python-d1-synth, max_messages=1, timeout=10s" in output
        assert "Received MIDI messages: note_on:60:velocity=96:channel=1" in output
        assert "Rendered sequence events: C4@0.000s" in output

    def test_midi_play_virtual_verbose_prints_multi_note_region_sequence(self, monkeypatch, capsys) -> None:
        class FakeAudioSelector:
            def select(self, cli_device):
                return AudioDeviceSelection(sounddevice_value="Scarlett 8i6 USB", source="cli")

        class FakeVirtualMidiAudioTrigger:
            def trigger(self, settings):
                parser = NoteParser()
                return VirtualMidiAudioTriggerResult(
                    port_name=settings.port_name,
                    received_message_count=6,
                    played_event_count=3,
                    audio_frame_count=22050,
                    sample_rate=44100,
                    message="Played 3 MIDI-triggered note events from virtual MIDI port python-d1-synth.",
                    received_messages=(
                        MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=0.0),
                        MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.1),
                        MidiMessage(message_type="note_on", note_number=62, velocity=96, channel=1, time_seconds=0.2),
                        MidiMessage(message_type="note_off", note_number=62, velocity=0, channel=1, time_seconds=0.3),
                        MidiMessage(message_type="note_on", note_number=64, velocity=90, channel=1, time_seconds=0.4),
                        MidiMessage(message_type="note_off", note_number=64, velocity=0, channel=1, time_seconds=0.5),
                    ),
                    played_events=(
                        NoteEvent(note=parser.parse("C4"), duration_seconds=0.1, velocity=100 / 127, start_seconds=0.0),
                        NoteEvent(note=parser.parse("D4"), duration_seconds=0.1, velocity=96 / 127, start_seconds=0.2),
                        NoteEvent(note=parser.parse("E4"), duration_seconds=0.1, velocity=90 / 127, start_seconds=0.4),
                    ),
                )

        monkeypatch.setattr(synth.cli, "AudioDeviceSelector", FakeAudioSelector)
        monkeypatch.setattr(synth.cli, "VirtualMidiAudioTrigger", FakeVirtualMidiAudioTrigger)

        exit_code = SynthCli().run(
            [
                "midi",
                "play-virtual",
                "--port-name",
                "python-d1-synth",
                "--audio-device",
                "Scarlett 8i6 USB",
                "--max-messages",
                "16",
                "--timeout",
                "10",
                "--debuglevel",
                "verbose",
            ]
        )

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "Played 3 MIDI-triggered note events from virtual MIDI port python-d1-synth." in output
        assert "Received MIDI messages: note_on:60:velocity=100:channel=1" in output
        assert "Rendered sequence events: C4@0.000s, D4@0.200s, E4@0.400s" in output

    def test_midi_play_virtual_reports_zero_received_messages(self, monkeypatch, capsys) -> None:
        class FakeAudioSelector:
            def select(self, cli_device):
                return AudioDeviceSelection(sounddevice_value=None, source="none")

        class FakeVirtualMidiAudioTrigger:
            def trigger(self, settings):
                return VirtualMidiAudioTriggerResult(
                    port_name=settings.port_name,
                    received_message_count=0,
                    played_event_count=0,
                    audio_frame_count=0,
                    sample_rate=44100,
                    message="Received 0 MIDI note messages from virtual MIDI port python-d1-synth; no audio played.",
                )

        monkeypatch.setattr(synth.cli, "AudioDeviceSelector", FakeAudioSelector)
        monkeypatch.setattr(synth.cli, "VirtualMidiAudioTrigger", FakeVirtualMidiAudioTrigger)

        exit_code = SynthCli().run(
            [
                "midi",
                "play-virtual",
                "--port-name",
                "python-d1-synth",
                "--max-messages",
                "1",
                "--timeout",
                "10",
                "--debuglevel",
                "verbose",
            ]
        )

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "Received 0 MIDI note messages from virtual MIDI port python-d1-synth; no audio played." in output

    def test_midi_play_virtual_handles_keyboard_interrupt(self, monkeypatch, capsys) -> None:
        class FakeAudioSelector:
            def select(self, cli_device):
                return AudioDeviceSelection(sounddevice_value=None, source="none")

        class FakeVirtualMidiAudioTrigger:
            def trigger(self, settings):
                raise KeyboardInterrupt

        monkeypatch.setattr(synth.cli, "AudioDeviceSelector", FakeAudioSelector)
        monkeypatch.setattr(synth.cli, "VirtualMidiAudioTrigger", FakeVirtualMidiAudioTrigger)

        exit_code = SynthCli().run(
            [
                "midi",
                "play-virtual",
                "--port-name",
                "python-d1-synth",
                "--max-messages",
                "2",
                "--timeout",
                "10",
                "--debuglevel",
                "light",
            ]
        )

        captured = capsys.readouterr()
        assert exit_code == 130
        assert "Opening virtual MIDI input port: python-d1-synth" in captured.out
        assert "Virtual MIDI audio trigger interrupted by user." in captured.err

    def test_midi_play_stream_triggers_near_realtime_audio_from_virtual_port(self, monkeypatch, capsys) -> None:
        class FakeAudioSelector:
            def select(self, cli_device):
                assert cli_device == "Scarlett 8i6 USB"
                return AudioDeviceSelection(sounddevice_value="Scarlett 8i6 USB", source="cli")

        class FakeStreamingMidiAudioTrigger:
            def trigger(self, settings):
                assert settings.port_name == "python-d1-synth"
                assert settings.max_messages == 4
                assert settings.timeout_seconds == 5.0
                assert settings.poll_interval_seconds == 0.002
                assert settings.note_duration_seconds == 0.2
                assert settings.voice_mode is StreamingVoiceMode.FIXED
                assert settings.dedupe_window_seconds == 0.04
                assert settings.audio_device == "Scarlett 8i6 USB"
                parser = NoteParser()
                return StreamingMidiAudioTriggerResult(
                    port_name=settings.port_name,
                    received_message_count=4,
                    played_event_count=2,
                    audio_frame_count=17640,
                    sample_rate=44100,
                    message=(
                        "Streamed 2 MIDI-triggered note events from virtual MIDI port python-d1-synth; "
                        "suppressed 2 duplicate MIDI messages."
                    ),
                    received_messages=(
                        MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=0.0),
                        MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.1),
                        MidiMessage(message_type="note_on", note_number=62, velocity=90, channel=1, time_seconds=0.2),
                        MidiMessage(message_type="note_off", note_number=62, velocity=0, channel=1, time_seconds=0.3),
                    ),
                    played_events=(
                        NoteEvent(note=parser.parse("C4"), duration_seconds=0.2, velocity=100 / 127, start_seconds=0.0),
                        NoteEvent(note=parser.parse("D4"), duration_seconds=0.2, velocity=90 / 127, start_seconds=0.2),
                    ),
                    suppressed_duplicate_count=2,
                )

        monkeypatch.setattr(synth.cli, "AudioDeviceSelector", FakeAudioSelector)
        monkeypatch.setattr(synth.cli, "StreamingMidiAudioTrigger", FakeStreamingMidiAudioTrigger)

        exit_code = SynthCli().run(
            [
                "midi",
                "play-stream",
                "--port-name",
                "python-d1-synth",
                "--audio-device",
                "Scarlett 8i6 USB",
                "--max-messages",
                "4",
                "--timeout",
                "5",
                "--poll-interval",
                "0.002",
                "--note-duration",
                "0.2",
                "--dedupe-window",
                "0.04",
                "--debuglevel",
                "verbose",
            ]
        )

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "Opening streaming virtual MIDI input port: python-d1-synth" in output
        assert "polyphonic chord batches are mixed" in output
        assert "Streaming MIDI audio trigger settings: port=python-d1-synth" in output
        assert "voice_mode=fixed" in output
        assert "dedupe_window=0.04s" in output
        assert "chord_window=0.02s" in output
        assert "suppressed 2 duplicate MIDI messages" in output
        assert "Received MIDI messages: note_on:60:velocity=100:channel=1" in output
        assert "Streamed sequence events: C4@0.000s, D4@0.200s" in output
        assert "Streamed note durations: C4@0.000s/0.200s, D4@0.200s/0.200s" in output
        assert "Suppressed duplicate MIDI messages: 2" in output

    def test_midi_play_stream_gated_mode_passes_voice_mode_and_reports_durations(self, monkeypatch, capsys) -> None:
        class FakeAudioSelector:
            def select(self, cli_device):
                assert cli_device == "Scarlett 8i6 USB"
                return AudioDeviceSelection(sounddevice_value="Scarlett 8i6 USB", source="cli")

        class FakeStreamingMidiAudioTrigger:
            def trigger(self, settings):
                assert settings.voice_mode is StreamingVoiceMode.GATED
                assert settings.note_duration_seconds == 0.3
                assert settings.chord_window_seconds == 0.04
                assert settings.audio_device == "Scarlett 8i6 USB"
                parser = NoteParser()
                return StreamingMidiAudioTriggerResult(
                    port_name=settings.port_name,
                    received_message_count=4,
                    played_event_count=2,
                    audio_frame_count=35280,
                    sample_rate=44100,
                    message=(
                        "Streamed 2 MIDI-triggered note events from virtual MIDI port python-d1-synth; "
                        "suppressed 0 duplicate MIDI messages."
                    ),
                    received_messages=(
                        MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=0.0),
                        MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.5),
                    ),
                    played_events=(
                        NoteEvent(note=parser.parse("C4"), duration_seconds=0.5, velocity=100 / 127, start_seconds=0.0),
                        NoteEvent(note=parser.parse("D4"), duration_seconds=0.3, velocity=90 / 127, start_seconds=0.7),
                    ),
                    suppressed_duplicate_count=0,
                )

        monkeypatch.setattr(synth.cli, "AudioDeviceSelector", FakeAudioSelector)
        monkeypatch.setattr(synth.cli, "StreamingMidiAudioTrigger", FakeStreamingMidiAudioTrigger)

        exit_code = SynthCli().run(
            [
                "midi",
                "play-stream",
                "--port-name",
                "python-d1-synth",
                "--audio-device",
                "Scarlett 8i6 USB",
                "--voice-mode",
                "gated",
                "--note-duration",
                "0.3",
                "--chord-window",
                "0.04",
                "--debuglevel",
                "verbose",
            ]
        )

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "polyphonic chord batches are mixed" in output
        assert "voice_mode=gated" in output
        assert "chord_window=0.04s" in output
        assert "Streamed note durations: C4@0.000s/0.500s, D4@0.700s/0.300s" in output

    def test_midi_play_stream_sustained_mode_passes_voice_mode_and_reports_lifecycle(self, monkeypatch, capsys) -> None:
        class FakeAudioSelector:
            def select(self, cli_device):
                assert cli_device == "Scarlett 8i6 USB"
                return AudioDeviceSelection(sounddevice_value="Scarlett 8i6 USB", source="cli")

        class FakeStreamingMidiAudioTrigger:
            def trigger(self, settings):
                assert settings.voice_mode is StreamingVoiceMode.SUSTAINED
                assert settings.audio_device == "Scarlett 8i6 USB"
                assert settings.pitch_bend_range_semitones == 12.0
                assert settings.pitch_bend_channel_mode is PitchBendChannelMode.OMNI
                assert settings.max_control_messages == 2048
                assert settings.modulation_vibrato_depth_semitones == 0.75
                assert settings.modulation_vibrato_rate_hz == 6.5
                assert settings.run_until_interrupted is False
                assert settings.release_time_seconds == 0.08
                parser = NoteParser()
                return StreamingMidiAudioTriggerResult(
                    port_name=settings.port_name,
                    received_message_count=3,
                    played_event_count=1,
                    audio_frame_count=88200,
                    sample_rate=44100,
                    message=(
                        "Streamed 1 MIDI-triggered note events from virtual MIDI port python-d1-synth; "
                        "suppressed 0 duplicate MIDI messages."
                    ),
                    received_messages=(
                        MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=0.0),
                        MidiMessage(
                            message_type="pitch_bend",
                            note_number=0,
                            velocity=0,
                            channel=1,
                            time_seconds=1.0,
                            pitch_bend_value=4096,
                        ),
                        MidiMessage(
                            message_type="control_change",
                            note_number=0,
                            velocity=0,
                            channel=1,
                            time_seconds=1.5,
                            control_number=1,
                            control_value=96,
                        ),
                        MidiMessage(
                            message_type="control_change",
                            note_number=0,
                            velocity=0,
                            channel=1,
                            time_seconds=1.6,
                            control_number=64,
                            control_value=127,
                        ),
                        MidiMessage(message_type="note_off", note_number=60, velocity=64, channel=1, time_seconds=2.0),
                    ),
                    played_events=(
                        NoteEvent(note=parser.parse("C4"), duration_seconds=2.0, velocity=100 / 127, start_seconds=0.0),
                    ),
                    suppressed_duplicate_count=0,
                )

        monkeypatch.setattr(synth.cli, "AudioDeviceSelector", FakeAudioSelector)
        monkeypatch.setattr(synth.cli, "StreamingMidiAudioTrigger", FakeStreamingMidiAudioTrigger)

        exit_code = SynthCli().run(
            [
                "midi",
                "play-stream",
                "--port-name",
                "python-d1-synth",
                "--audio-device",
                "Scarlett 8i6 USB",
                "--voice-mode",
                "sustained",
                "--pitch-bend-range",
                "12",
                "--pitch-bend-channel-mode",
                "omni",
                "--max-control-messages",
                "2048",
                "--modulation-vibrato-depth",
                "0.75",
                "--modulation-vibrato-rate",
                "6.5",
                "--release-time",
                "0.08",
                "--debuglevel",
                "verbose",
            ]
        )

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "Sustained MVP note: note_on starts a streaming voice and note_off stops it" in output
        assert "voice_mode=sustained" in output
        assert "pitch_bend_range=12st" in output
        assert "pitch_bend_channel_mode=omni" in output
        assert "max_control_messages=2048" in output
        assert "modulation_vibrato_depth=0.75st" in output
        assert "modulation_vibrato_rate=6.5Hz" in output
        assert "until_interrupt=false" in output
        assert "release_time=0.08s" in output
        assert "pitch_bend:4096:channel=1" in output
        assert "control_change:1:96:channel=1" in output
        assert "Streamed note durations: C4@0.000s/2.000s" in output
        assert "Total streamed audio frames: 88200, sample_rate=44100 Hz" in output
        assert "CC64 sustain pedal holds released voices" in output
        assert "release-time softens note-off" in output
        assert "control_change:64:127:channel=1" in output

    def test_midi_play_stream_until_interrupt_passes_performance_mode(self, monkeypatch, capsys) -> None:
        class FakeAudioSelector:
            def select(self, cli_device):
                return AudioDeviceSelection(sounddevice_value="Scarlett 8i6 USB", source="cli")

        class FakeStreamingMidiAudioTrigger:
            def trigger(self, settings):
                assert settings.run_until_interrupted is True
                assert settings.max_messages == 10000
                assert settings.timeout_seconds == 600.0
                return StreamingMidiAudioTriggerResult(
                    port_name=settings.port_name,
                    received_message_count=0,
                    played_event_count=0,
                    audio_frame_count=0,
                    sample_rate=44100,
                    message=(
                        "Received 0 MIDI note messages from streaming virtual MIDI port "
                        "python-d1-synth; no audio played."
                    ),
                )

        monkeypatch.setattr(synth.cli, "AudioDeviceSelector", FakeAudioSelector)
        monkeypatch.setattr(synth.cli, "StreamingMidiAudioTrigger", FakeStreamingMidiAudioTrigger)

        exit_code = SynthCli().run(
            [
                "midi",
                "play-stream",
                "--port-name",
                "python-d1-synth",
                "--audio-device",
                "Scarlett 8i6 USB",
                "--max-messages",
                "10000",
                "--timeout",
                "600",
                "--voice-mode",
                "sustained",
                "--until-interrupt",
                "--debuglevel",
                "verbose",
            ]
        )

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "Performance mode: running until Ctrl-C" in output
        assert "until_interrupt=true" in output

    def test_midi_play_stream_handles_keyboard_interrupt(self, monkeypatch, capsys) -> None:
        class FakeAudioSelector:
            def select(self, cli_device):
                return AudioDeviceSelection(sounddevice_value=None, source="none")

        class FakeStreamingMidiAudioTrigger:
            def trigger(self, settings):
                raise KeyboardInterrupt

        monkeypatch.setattr(synth.cli, "AudioDeviceSelector", FakeAudioSelector)
        monkeypatch.setattr(synth.cli, "StreamingMidiAudioTrigger", FakeStreamingMidiAudioTrigger)

        exit_code = SynthCli().run(
            [
                "midi",
                "play-stream",
                "--port-name",
                "python-d1-synth",
                "--timeout",
                "10",
                "--debuglevel",
                "light",
            ]
        )

        captured = capsys.readouterr()
        assert exit_code == 130
        assert "Opening streaming virtual MIDI input port: python-d1-synth" in captured.out
        assert "Streaming MIDI audio trigger interrupted by user." in captured.err
