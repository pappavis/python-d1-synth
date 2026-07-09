import numpy as np

from synth.oscillators import Oscillator, OscillatorSettings, Waveform


class TestOscillator:
    def test_sine_sample_count_and_amplitude(self) -> None:
        oscillator = Oscillator(OscillatorSettings(waveform=Waveform.SINE, sample_rate=44100, amplitude=0.2))

        samples = oscillator.generate(frequency_hz=440.0, duration_seconds=1.0)

        assert samples.shape == (44100,)
        assert np.max(samples) <= 0.2
        assert np.min(samples) >= -0.2

    def test_saw_sample_count_amplitude_and_ramp_levels(self) -> None:
        oscillator = Oscillator(OscillatorSettings(waveform=Waveform.SAW, sample_rate=44100, amplitude=0.2))

        samples = oscillator.generate(frequency_hz=440.0, duration_seconds=0.25)

        assert samples.shape == (11025,)
        assert np.max(samples) <= 0.2
        assert np.min(samples) >= -0.2
        assert np.any(samples > 0.0)
        assert np.any(samples < 0.0)
        assert len(np.unique(np.round(samples, 4))) > 10

    def test_square_sample_count_amplitude_and_levels(self) -> None:
        oscillator = Oscillator(OscillatorSettings(waveform=Waveform.SQUARE, sample_rate=44100, amplitude=0.2))

        samples = oscillator.generate(frequency_hz=440.0, duration_seconds=0.25)

        assert samples.shape == (11025,)
        assert np.max(samples) == np.float32(0.2)
        assert np.min(samples) == np.float32(-0.2)
        assert set(np.unique(samples)) == {np.float32(-0.2), np.float32(0.2)}
