# Bestand: test_config.py
# Versienummer: 0.1.0
# Doel: Tests voor YAML patch configuratie en MIDI performance defaults.
# Sprint: Future MIDI/DAW
# User-Story: US-042 MIDI Performance Patch YAML Config
# Actie: US-042-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-042

import pytest

from synth.config import PatchConfigLoader
from synth.oscillators import Waveform


class TestPatchConfigLoader:
    def test_loads_midi_default_device(self) -> None:
        config = PatchConfigLoader().from_mapping(
            {
                "oscillator": {"waveform": "sine", "note": "C3", "amplitude": 0.2},
                "midi": {"default_input_device": "Arturia KeyLab Mk3"},
            }
        )

        assert config.oscillator.waveform is Waveform.SINE
        assert config.midi.default_input_device == "Arturia KeyLab Mk3"

    def test_loads_midi_performance_defaults(self) -> None:
        config = PatchConfigLoader().from_mapping(
            {
                "debuglevel": "verbose",
                "oscillator": {"waveform": "sine", "note": "C3", "amplitude": 0.2},
                "midi": {
                    "performance": {
                        "port_name": "python-d1-synth",
                        "audio_device": "Scarlett 8i6 USB",
                        "voice_mode": "sustained",
                        "max_messages": 10000,
                        "timeout_seconds": 600,
                        "poll_interval_seconds": 0.005,
                        "note_duration_seconds": 0.25,
                        "dedupe_window_seconds": 0.03,
                        "chord_window_seconds": 0.08,
                        "pitch_bend_range_semitones": 2,
                        "pitch_bend_channel_mode": "omni",
                        "max_control_messages": 20000,
                        "modulation_vibrato_depth_semitones": 0.25,
                        "modulation_vibrato_rate_hz": 5,
                        "run_until_interrupted": True,
                        "attack_time_seconds": 0.02,
                        "decay_time_seconds": 0.12,
                        "sustain_level": 0.6,
                        "release_time_seconds": 0.08,
                        "sample_rate": 44100,
                        "waveform": "sine",
                        "amplitude": 0.2,
                        "channel": "stereo",
                    }
                },
            }
        )

        performance = config.midi.performance
        assert performance.port_name == "python-d1-synth"
        assert performance.audio_device == "Scarlett 8i6 USB"
        assert performance.voice_mode == "sustained"
        assert performance.max_messages == 10000
        assert performance.timeout_seconds == 600.0
        assert performance.chord_window_seconds == 0.08
        assert performance.pitch_bend_channel_mode == "omni"
        assert performance.run_until_interrupted is True
        assert performance.attack_time_seconds == 0.02
        assert performance.sustain_level == 0.6

    def test_rejects_non_mapping_midi_performance_section(self) -> None:
        with pytest.raises(ValueError, match="midi.performance must be a mapping"):
            PatchConfigLoader().from_mapping({"midi": {"performance": "sustained"}})
