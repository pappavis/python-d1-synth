# Bestand: test_audio.py
# Versienummer: 0.1.0
# Doel: Tests voor audio routing, device selectie en sustained streaming output.
# Sprint: Future MIDI/DAW
# User-Story: US-035 Sustained Note Audio Engine
# Actie: US-035-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-035

import numpy as np

from synth.audio import (
    AudioBuffer,
    AudioDeviceScanner,
    AudioDeviceSelector,
    ChannelRouter,
    OutputChannel,
    SoundDeviceAudioPlayer,
    SoundDeviceSustainedAudioPlayer,
    SustainedAudioPlayerSettings,
)
from synth.oscillators import Waveform


class TestChannelRouter:
    def test_stereo_channel_copies_mono_to_both_channels(self) -> None:
        mono = np.array([0.1, -0.2], dtype=np.float32)

        stereo = ChannelRouter().route(mono, OutputChannel.STEREO)

        assert stereo.shape == (2, 2)
        assert np.allclose(stereo[:, 0], mono)
        assert np.allclose(stereo[:, 1], mono)

    def test_left_channel_mutes_right(self) -> None:
        mono = np.array([0.1, -0.2], dtype=np.float32)

        stereo = ChannelRouter().route(mono, OutputChannel.LEFT)

        assert stereo.shape == (2, 2)
        assert np.allclose(stereo[:, 0], mono)
        assert np.allclose(stereo[:, 1], 0.0)

    def test_right_channel_mutes_left(self) -> None:
        mono = np.array([0.1, -0.2], dtype=np.float32)

        stereo = ChannelRouter().route(mono, OutputChannel.RIGHT)

        assert stereo.shape == (2, 2)
        assert np.allclose(stereo[:, 0], 0.0)
        assert np.allclose(stereo[:, 1], mono)


class TestAudioDeviceSelector:
    def test_numeric_cli_device_becomes_integer(self) -> None:
        selection = AudioDeviceSelector().select("2")

        assert selection.sounddevice_value == 2
        assert selection.source == "cli"

    def test_named_cli_device_stays_string(self) -> None:
        selection = AudioDeviceSelector().select("MacBook Speakers")

        assert selection.sounddevice_value == "MacBook Speakers"
        assert selection.source == "cli"

    def test_empty_cli_device_uses_default(self) -> None:
        selection = AudioDeviceSelector().select(None)

        assert selection.sounddevice_value is None
        assert selection.source == "default"


class TestAudioDeviceScanner:
    def test_scan_returns_diagnostic_when_sounddevice_query_fails(self, monkeypatch) -> None:
        class FakeSoundDevice:
            def query_devices(self):
                raise RuntimeError("PortAudio not available")

            def query_hostapis(self):
                return []

        monkeypatch.setitem(__import__("sys").modules, "sounddevice", FakeSoundDevice())

        result = AudioDeviceScanner().scan()

        assert result.devices == tuple()
        assert result.error_message == "sounddevice query failed: PortAudio not available"


class TestSoundDeviceAudioPlayer:
    def test_play_passes_selected_device(self, monkeypatch) -> None:
        calls = []

        class FakeSoundDevice:
            def play(self, samples, samplerate, device=None):
                calls.append(("play", samples.shape, samplerate, device))

            def wait(self):
                calls.append(("wait",))

        monkeypatch.setitem(__import__("sys").modules, "sounddevice", FakeSoundDevice())
        buffer = AudioBuffer(samples=np.zeros((2, 2), dtype=np.float32), sample_rate=44100)

        SoundDeviceAudioPlayer().play(buffer, device=3)

        assert calls == [("play", (2, 2), 44100, 3), ("wait",)]


class TestSoundDeviceSustainedAudioPlayer:
    def test_callback_renders_active_voice_until_note_off(self) -> None:
        player = SoundDeviceSustainedAudioPlayer()
        settings = SustainedAudioPlayerSettings(
            sample_rate=100,
            waveform=Waveform.SINE,
            amplitude=0.2,
            channel=OutputChannel.STEREO,
        )
        player._settings = settings

        player.note_on((1, 60), frequency_hz=10.0, velocity=1.0)
        outdata = np.zeros((20, 2), dtype=np.float32)

        player._callback(outdata, 20, None, None)

        assert np.any(np.abs(outdata[:, 0]) > 0.0)
        assert np.allclose(outdata[:, 0], outdata[:, 1])
        assert player.active_voice_count() == 1

        player.note_off((1, 60))
        silent_outdata = np.ones((20, 2), dtype=np.float32)

        player._callback(silent_outdata, 20, None, None)

        assert np.allclose(silent_outdata, 0.0)
        assert player.active_voice_count() == 0

    def test_start_and_stop_manage_sounddevice_stream(self, monkeypatch) -> None:
        calls = []

        class FakeOutputStream:
            def __init__(self, samplerate, channels, dtype, device, callback):
                calls.append(("create", samplerate, channels, dtype, device, callable(callback)))

            def start(self):
                calls.append(("start",))

            def stop(self):
                calls.append(("stop",))

            def close(self):
                calls.append(("close",))

        class FakeSoundDevice:
            OutputStream = FakeOutputStream

        monkeypatch.setitem(__import__("sys").modules, "sounddevice", FakeSoundDevice())
        player = SoundDeviceSustainedAudioPlayer()

        player.start(
            SustainedAudioPlayerSettings(
                sample_rate=44100,
                waveform=Waveform.SINE,
                amplitude=0.2,
                channel=OutputChannel.STEREO,
                device="Scarlett 8i6 USB",
            )
        )
        frames = player.stop()

        assert frames == 0
        assert calls == [
            ("create", 44100, 2, "float32", "Scarlett 8i6 USB", True),
            ("start",),
            ("stop",),
            ("close",),
        ]
