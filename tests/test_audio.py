import numpy as np

from synth.audio import AudioBuffer, AudioDeviceScanner, AudioDeviceSelector, ChannelRouter, OutputChannel, SoundDeviceAudioPlayer


class TestChannelRouter:
    def test_left_channel_mutes_right(self) -> None:
        mono = np.array([0.1, -0.2], dtype=np.float32)

        stereo = ChannelRouter().route(mono, OutputChannel.LEFT)

        assert stereo.shape == (2, 2)
        assert np.allclose(stereo[:, 0], mono)
        assert np.allclose(stereo[:, 1], 0.0)


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
