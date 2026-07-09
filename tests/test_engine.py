import numpy as np

from synth.audio import OutputChannel
from synth.engine import SynthEngine, SynthEngineSettings
from synth.notes import NoteEvent, NoteParser
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

    def test_render_note_left_channel_keeps_right_silent(self) -> None:
        note = NoteParser().parse("C3")
        engine = SynthEngine(
            SynthEngineSettings(
                sample_rate=44100,
                waveform=Waveform.SINE,
                amplitude=0.2,
                channel=OutputChannel.LEFT,
            )
        )

        buffer = engine.render_note(NoteEvent(note=note, duration_seconds=0.1, velocity=1.0))

        assert np.any(np.abs(buffer.samples[:, 0]) > 0.0)
        assert np.allclose(buffer.samples[:, 1], 0.0)

    def test_render_note_right_channel_keeps_left_silent(self) -> None:
        note = NoteParser().parse("C3")
        engine = SynthEngine(
            SynthEngineSettings(
                sample_rate=44100,
                waveform=Waveform.SINE,
                amplitude=0.2,
                channel=OutputChannel.RIGHT,
            )
        )

        buffer = engine.render_note(NoteEvent(note=note, duration_seconds=0.1, velocity=1.0))

        assert np.allclose(buffer.samples[:, 0], 0.0)
        assert np.any(np.abs(buffer.samples[:, 1]) > 0.0)
