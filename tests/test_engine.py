# Bestand: test_engine.py
# Versienummer: 0.1.0
# Doel: Tests voor synth rendering en polyphonic voice mixing.
# Sprint: Future MIDI/DAW
# User-Story: US-034 Polyphonic Voice Mixer En Triads
# Actie: US-034-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-034

import numpy as np

from synth.audio import OutputChannel
from synth.engine import PolyphonicVoiceMixer, SynthEngine, SynthEngineSettings
from synth.notes import NoteEvent, NoteParser, NoteSequence
from synth.oscillators import Oscillator, OscillatorSettings, Waveform


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

    def test_polyphonic_voice_mixer_mixes_three_simultaneous_notes_as_triad(self) -> None:
        parser = NoteParser()
        sequence = NoteSequence(
            events=(
                NoteEvent(note=parser.parse("C4"), duration_seconds=0.25, velocity=0.8, start_seconds=0.0),
                NoteEvent(note=parser.parse("E4"), duration_seconds=0.25, velocity=0.8, start_seconds=0.0),
                NoteEvent(note=parser.parse("G4"), duration_seconds=0.25, velocity=0.8, start_seconds=0.0),
            )
        )
        engine = SynthEngine(
            SynthEngineSettings(
                sample_rate=44100,
                waveform=Waveform.SINE,
                amplitude=0.2,
                channel=OutputChannel.STEREO,
            )
        )

        buffer = engine.render_sequence(sequence)

        assert buffer.samples.shape == (11025, 2)
        assert np.any(np.abs(buffer.samples[:, 0]) > 0.0)
        assert np.allclose(buffer.samples[:, 0], buffer.samples[:, 1])
        assert np.max(buffer.samples) <= 1.0

    def test_polyphonic_voice_mixer_offsets_later_notes_inside_mix(self) -> None:
        parser = NoteParser()
        oscillator = Oscillator(OscillatorSettings(waveform=Waveform.SINE, sample_rate=100, amplitude=0.2))
        mixer = PolyphonicVoiceMixer(oscillator)
        events = (
            NoteEvent(note=parser.parse("C4"), duration_seconds=0.1, velocity=1.0, start_seconds=0.0),
            NoteEvent(note=parser.parse("E4"), duration_seconds=0.1, velocity=1.0, start_seconds=0.1),
        )

        mix = mixer.mix(events, total_samples=20, sample_rate=100)

        assert mix.shape == (20,)
        assert np.any(np.abs(mix[:10]) > 0.0)
        assert np.any(np.abs(mix[10:]) > 0.0)
