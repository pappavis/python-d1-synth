import numpy as np

from synth.audio import AudioDevice
import synth.cli
from synth.cli import SynthCli
from synth.midi import MidiDevice


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
                    },
                )()

        monkeypatch.setattr(synth.cli, "MidiDeviceScanner", FakeScanner)

        exit_code = SynthCli().run(["midi", "list-devices", "--unsafe-rtmidi-scan", "--debuglevel", "light"])

        output = capsys.readouterr().out
        assert exit_code == 0
        assert "MIDI backend failed while scanning devices." in output
        assert "If Logic Pro shows devices but Python does not" in output
