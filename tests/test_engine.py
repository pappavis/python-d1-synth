import numpy as np

from synth.audio import OutputChannel
from synth.engine import SynthEngine, SynthEngineSettings
from synth.notes import NoteParser
from synth.oscillators import Waveform


class TestSynthEngine:
    def test_render_sequence_uses_total_duration_and_stereo_shape(self) -> None:
        sequence = NoteParser().parse_testsequence("ACGD", duration_seconds=0.25)
        engine = SynthEngine(
            SynthEngineSettings(
                sample_rate=44100,
                waveform=Waveform.SINE,
                amplitude=0.2,
                channel=OutputChannel.STEREO,
            )
        )

        buffer = engine.render_sequence(sequence)

        assert buffer.sample_rate == 44100
        assert buffer.samples.shape == (44100, 2)
        assert np.max(buffer.samples) <= 1.0
        assert np.min(buffer.samples) >= -1.0
