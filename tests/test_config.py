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

