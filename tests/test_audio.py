# Bestand: test_audio.py
# Versienummer: 0.1.0
# Doel: Tests voor audio routing, device selectie en sustained streaming output.
# Sprint: Future MIDI/DAW
# User-Story: US-041 Amp Envelope ADSR Parameters
# Actie: US-041-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-041

import numpy as np
import pytest

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
    def test_sustained_settings_validate_adsr_parameters(self) -> None:
        with pytest.raises(ValueError, match="attack_seconds"):
            SustainedAudioPlayerSettings(
                sample_rate=100,
                waveform=Waveform.SINE,
                amplitude=0.2,
                channel=OutputChannel.STEREO,
                attack_seconds=-0.01,
            )
        with pytest.raises(ValueError, match="decay_seconds"):
            SustainedAudioPlayerSettings(
                sample_rate=100,
                waveform=Waveform.SINE,
                amplitude=0.2,
                channel=OutputChannel.STEREO,
                decay_seconds=-0.01,
            )
        with pytest.raises(ValueError, match="sustain_level"):
            SustainedAudioPlayerSettings(
                sample_rate=100,
                waveform=Waveform.SINE,
                amplitude=0.2,
                channel=OutputChannel.STEREO,
                sustain_level=1.1,
            )

    def test_callback_renders_active_voice_until_note_off(self) -> None:
        player = SoundDeviceSustainedAudioPlayer()
        settings = SustainedAudioPlayerSettings(
            sample_rate=100,
            waveform=Waveform.SINE,
            amplitude=0.2,
            channel=OutputChannel.STEREO,
            release_seconds=0.0,
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

    def test_callback_fades_released_voice_before_removing_it(self) -> None:
        player = SoundDeviceSustainedAudioPlayer()
        settings = SustainedAudioPlayerSettings(
            sample_rate=100,
            waveform=Waveform.SQUARE,
            amplitude=0.2,
            channel=OutputChannel.STEREO,
            release_seconds=0.05,
        )
        player._settings = settings

        player.note_on((1, 60), frequency_hz=10.0, velocity=1.0)
        player.note_off((1, 60))
        release_outdata = np.zeros((5, 2), dtype=np.float32)

        player._callback(release_outdata, 5, None, None)

        assert np.max(np.abs(release_outdata[:, 0])) > 0.0
        assert np.max(np.abs(release_outdata[-1:, 0])) < np.max(np.abs(release_outdata[:1, 0]))
        assert player.active_voice_count() == 0

    def test_callback_applies_attack_decay_sustain_envelope(self) -> None:
        player = SoundDeviceSustainedAudioPlayer()
        settings = SustainedAudioPlayerSettings(
            sample_rate=100,
            waveform=Waveform.SQUARE,
            amplitude=1.0,
            channel=OutputChannel.STEREO,
            attack_seconds=0.04,
            decay_seconds=0.04,
            sustain_level=0.5,
            release_seconds=0.0,
        )
        player._settings = settings

        player.note_on((1, 60), frequency_hz=1.0, velocity=1.0)
        outdata = np.zeros((10, 2), dtype=np.float32)

        player._callback(outdata, 10, None, None)

        assert np.allclose(outdata[:, 0], [0.25, 0.5, 0.75, 1.0, 0.875, 0.75, 0.625, 0.5, 0.5, 0.5])
        assert np.allclose(outdata[:, 0], outdata[:, 1])

    def test_release_starts_from_current_adsr_level(self) -> None:
        player = SoundDeviceSustainedAudioPlayer()
        settings = SustainedAudioPlayerSettings(
            sample_rate=100,
            waveform=Waveform.SQUARE,
            amplitude=1.0,
            channel=OutputChannel.STEREO,
            attack_seconds=0.04,
            decay_seconds=0.0,
            sustain_level=1.0,
            release_seconds=0.04,
        )
        player._settings = settings

        player.note_on((1, 60), frequency_hz=1.0, velocity=1.0)
        player._callback(np.zeros((2, 2), dtype=np.float32), 2, None, None)
        player.note_off((1, 60))
        release_outdata = np.zeros((4, 2), dtype=np.float32)

        player._callback(release_outdata, 4, None, None)

        assert np.allclose(release_outdata[:, 0], [0.75, 0.5625, 0.375, 0.1875])
        assert player.active_voice_count() == 0

    def test_pitch_bend_updates_only_matching_channel_voice_frequency(self) -> None:
        player = SoundDeviceSustainedAudioPlayer()
        player.note_on((1, 60), frequency_hz=100.0, velocity=1.0)
        player.note_on((2, 60), frequency_hz=200.0, velocity=1.0)

        player.pitch_bend(channel=1, semitones=12.0)

        assert player._voice_by_id[(1, 60)].base_frequency_hz == 100.0
        assert player._voice_by_id[(1, 60)].frequency_hz == 200.0
        assert player._voice_by_id[(2, 60)].frequency_hz == 200.0

    def test_modulation_updates_only_matching_channel_voice_vibrato(self) -> None:
        player = SoundDeviceSustainedAudioPlayer()
        player.note_on((1, 60), frequency_hz=100.0, velocity=1.0)
        player.note_on((2, 60), frequency_hz=200.0, velocity=1.0)

        player.modulation(channel=1, depth_semitones=0.5, rate_hz=6.0)

        assert player._voice_by_id[(1, 60)].modulation_depth_semitones == 0.5
        assert player._voice_by_id[(1, 60)].modulation_rate_hz == 6.0
        assert player._voice_by_id[(2, 60)].modulation_depth_semitones == 0.0

    def test_modulated_frequency_varies_around_current_frequency(self) -> None:
        player = SoundDeviceSustainedAudioPlayer()
        player.note_on((1, 60), frequency_hz=100.0, velocity=1.0)
        player.modulation(channel=1, depth_semitones=1.0, rate_hz=5.0)
        voice = player._voice_by_id[(1, 60)]

        frequencies = player._modulated_frequency(voice, np.linspace(0.0, 0.2, 200, dtype=np.float64))

        assert np.min(frequencies) < 100.0
        assert np.max(frequencies) > 100.0

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

    def test_abort_uses_stream_abort_for_interrupt_cleanup(self, monkeypatch) -> None:
        calls = []

        class FakeOutputStream:
            def __init__(self, samplerate, channels, dtype, device, callback):
                calls.append(("create", samplerate, channels, dtype, device, callable(callback)))

            def start(self):
                calls.append(("start",))

            def abort(self):
                calls.append(("abort",))

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
        frames = player.abort()

        assert frames == 0
        assert calls == [
            ("create", 44100, 2, "float32", "Scarlett 8i6 USB", True),
            ("start",),
            ("abort",),
            ("close",),
        ]
