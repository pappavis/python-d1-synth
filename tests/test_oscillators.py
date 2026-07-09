import numpy as np

from synth.oscillators import Oscillator, OscillatorSettings, Waveform


class TestOscillator:
    def test_sine_sample_count_and_amplitude(self) -> None:
        oscillator = Oscillator(OscillatorSettings(waveform=Waveform.SINE, sample_rate=44100, amplitude=0.2))

        samples = oscillator.generate(frequency_hz=440.0, duration_seconds=1.0)

        assert samples.shape == (44100,)
        assert np.max(samples) <= 0.2
        assert np.min(samples) >= -0.2

