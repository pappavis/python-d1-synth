import argparse
import sys
from pathlib import Path

from synth.audio import AudioDeviceScanner, AudioDeviceSelector, OutputChannel, SoundDeviceAudioPlayer
from synth.config import PatchConfigLoader
from synth.debug import DebugLevel, DebugReporter
from synth.engine import SynthEngine, SynthEngineSettings
from synth.midi import MidiDeviceScanner, MidiDeviceSelector
from synth.notes import NoteEvent, NoteParser, NoteSequence
from synth.oscillators import Waveform
from synth.wav_writer import WavWriter


class SynthCli:
    def __init__(self) -> None:
        self._parser = self._build_parser()

    def run(self, argv: list[str] | None = None) -> int:
        args = self._parser.parse_args(argv)
        return int(args.handler(args))

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog="python-d1-synth")
        subparsers = parser.add_subparsers(dest="command", required=True)

        play = subparsers.add_parser("play", help="Play a note or testsequence.")
        play.add_argument("--note")
        play.add_argument("--testsequence")
        play.add_argument("--duration", type=float, default=1.0)
        play.add_argument("--waveform", choices=[item.value for item in Waveform], default=Waveform.SINE.value)
        play.add_argument("--sample-rate", type=int, default=44100)
        play.add_argument("--channel", choices=[item.value for item in OutputChannel], default=OutputChannel.STEREO.value)
        play.add_argument("--debuglevel", choices=[item.value for item in DebugLevel], default=DebugLevel.NONE.value)
        play.add_argument("--midi-device")
        play.add_argument("--audio-device")
        play.set_defaults(handler=self._handle_play)

        audio = subparsers.add_parser("audio", help="Audio device utilities.")
        audio_subparsers = audio.add_subparsers(dest="audio_command", required=True)
        audio_devices = audio_subparsers.add_parser("list-devices", help="List detected audio devices.")
        audio_devices.add_argument("--debuglevel", choices=[item.value for item in DebugLevel], default=DebugLevel.NONE.value)
        audio_devices.set_defaults(handler=self._handle_audio_list_devices)

        render = subparsers.add_parser("render", help="Render a YAML patch to WAV.")
        render.add_argument("patch")
        render.add_argument("--output", required=True)
        render.add_argument("--debuglevel", choices=[item.value for item in DebugLevel])
        render.set_defaults(handler=self._handle_render)

        midi = subparsers.add_parser("midi", help="MIDI utilities.")
        midi_subparsers = midi.add_subparsers(dest="midi_command", required=True)
        list_devices = midi_subparsers.add_parser("list-devices", help="List detected MIDI devices.")
        list_devices.add_argument("--debuglevel", choices=[item.value for item in DebugLevel], default=DebugLevel.NONE.value)
        list_devices.add_argument("--unsafe-rtmidi-scan", action="store_true")
        list_devices.set_defaults(handler=self._handle_midi_list_devices)

        return parser

    def _handle_play(self, args: argparse.Namespace) -> int:
        reporter = DebugReporter(DebugLevel(args.debuglevel))
        parser = NoteParser()
        selector = MidiDeviceSelector()
        selection = selector.select(args.midi_device, None)
        if selection.selected_device is not None:
            reporter.light(f"Selected MIDI device from {selection.source}: {selection.selected_device}")
        audio_selection = AudioDeviceSelector().select(args.audio_device)
        if audio_selection.sounddevice_value is not None:
            reporter.light(f"Selected audio device from {audio_selection.source}: {audio_selection.sounddevice_value}")

        engine = SynthEngine(
            SynthEngineSettings(
                sample_rate=args.sample_rate,
                waveform=Waveform(args.waveform),
                amplitude=0.2,
                channel=OutputChannel(args.channel),
            )
        )

        if args.testsequence:
            reporter.light(f"Playing testsequence {args.testsequence}")
            sequence = parser.parse_testsequence(args.testsequence, args.duration)
            reporter.verbose(f"Sequence events: {self._format_sequence_events(sequence)}")
            buffer = engine.render_sequence(sequence)
        else:
            note_name = args.note if args.note else "C3"
            reporter.light(f"Playing note {note_name}")
            note = parser.parse(note_name)
            buffer = engine.render_note(NoteEvent(note=note, duration_seconds=args.duration, velocity=1.0))

        reporter.verbose(f"Audio buffer: {buffer.samples.shape[0]} frames, {buffer.sample_rate} Hz")
        try:
            SoundDeviceAudioPlayer().play(buffer, device=audio_selection.sounddevice_value)
        except RuntimeError as exc:
            print(f"Audio playback error: {exc}", file=sys.stderr)
            return 2
        return 0

    def _handle_render(self, args: argparse.Namespace) -> int:
        loader = PatchConfigLoader()
        config = loader.load(Path(args.patch))
        debuglevel = DebugLevel(args.debuglevel) if args.debuglevel else config.debuglevel
        reporter = DebugReporter(debuglevel)
        reporter.light(f"Rendering patch {args.patch} to {args.output}")

        note = NoteParser().parse(config.oscillator.note)
        engine = SynthEngine(
            SynthEngineSettings(
                sample_rate=config.sample_rate,
                waveform=config.oscillator.waveform,
                amplitude=config.oscillator.amplitude,
                channel=config.channel,
            )
        )
        event = NoteEvent(note=note, duration_seconds=config.duration_seconds, velocity=1.0)
        buffer = engine.render_note(event)
        WavWriter().write(Path(args.output), buffer)
        reporter.light("Render complete")
        return 0

    def _handle_midi_list_devices(self, args: argparse.Namespace) -> int:
        reporter = DebugReporter(DebugLevel(args.debuglevel))
        result = MidiDeviceScanner(allow_unsafe_native_scan=args.unsafe_rtmidi_scan).scan()
        devices = result.devices
        if not devices:
            if result.error_message is not None:
                reporter.light(result.error_message)
            reporter.light("No MIDI devices detected or optional MIDI backend is not installed.")
            print("No MIDI devices found.")
            return 0
        for device in devices:
            print(f"{device.identifier}\t{device.direction}\t{device.name}")
        return 0

    def _handle_audio_list_devices(self, args: argparse.Namespace) -> int:
        reporter = DebugReporter(DebugLevel(args.debuglevel))
        result = AudioDeviceScanner().scan()
        output_devices = tuple(device for device in result.devices if device.is_output())
        if not output_devices:
            if result.error_message is not None:
                reporter.light(result.error_message)
            reporter.light("No audio output devices detected or sounddevice could not query PortAudio.")
            print("No audio output devices found.")
            return 0
        print("id\toutputs\tdefault_samplerate\thost_api\tname")
        for device in output_devices:
            print(
                f"{device.identifier}\t{device.max_output_channels}\t"
                f"{device.default_sample_rate:.0f}\t{device.host_api}\t{device.name}"
            )
        return 0

    def _format_sequence_events(self, sequence: NoteSequence) -> str:
        return ", ".join(
            f"{event.note.name}{event.note.octave}@{event.start_seconds:.3f}s" for event in sequence.events
        )


def main(argv: list[str] | None = None) -> int:
    return SynthCli().run(argv)
