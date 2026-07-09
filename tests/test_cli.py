from synth.audio import AudioDevice
import synth.cli
from synth.cli import SynthCli


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
