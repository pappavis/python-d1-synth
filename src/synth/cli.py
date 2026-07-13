# Bestand: cli.py
# Versienummer: 0.1.0
# Doel: Commandline entrypoint voor playback, render, audio utilities en MIDI/DAW workflows.
# Sprint: Future MIDI/DAW
# User-Story: US-042 MIDI Performance Patch YAML Config
# Actie: US-042-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-042

import argparse
import importlib.util
import signal
import sys
from pathlib import Path

from synth.audio import AudioDeviceScanner, AudioDeviceSelector, OutputChannel, SoundDeviceAudioPlayer
from synth.config import MidiPerformanceConfig, PatchConfig, PatchConfigLoader
from synth.debug import DebugLevel, DebugReporter
from synth.engine import SynthEngine, SynthEngineSettings
from synth.midi import (
    LiveMidiInputReceiver,
    MidiAudioTrigger,
    MidiAudioTriggerSettings,
    MidiDeviceScanner,
    MidiDeviceSelector,
    MidiInputReceiveSettings,
    PitchBendChannelMode,
    StreamingMidiAudioTrigger,
    StreamingMidiAudioTriggerSettings,
    StreamingVoiceMode,
    UsbMidiHardwareInputAdapter,
    VirtualMidiAudioTrigger,
    VirtualMidiAudioTriggerSettings,
    VirtualMidiInputAdapter,
    VirtualMidiPortManager,
    VirtualMidiPortSettings,
)
from synth.notes import NoteEvent, NoteParser, NoteSequence
from synth.oscillators import Waveform
from synth.wav_writer import WavWriter


class SynthCli:
    """Commandline entrypoint for Sprint 1 synth workflows.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-004 Realtime CLI Playback
    - User Story: US-013 Channel Selection
    - Epic: EPIC-005 Configuratie En CLI
    - User Story: US-016 Debuglevel
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-020 Virtual MIDI Input Voor DAW
    - User Story: US-022 USB MIDI Hardware Input
    - User Story: US-025 MIDI Device Discovery En Default Selection
    - User Story: US-026 Live MIDI Input Receive Loop
    - User Story: US-027 Virtual MIDI Port Voor Logic/DAW
    - User Story: US-028 External MIDI Audio Trigger Integratie
    - User Story: US-029 Logic/DAW Virtual MIDI Naar Audio Trigger
    - User Story: US-030 Logic MIDI Region Multi-Note Playback
    - User Story: US-031 Live/Streaming MIDI Playback Loop
    - User Story: US-032 Duplicate MIDI Event Guard
    - User Story: US-033 Note Off Gated Voice Duration
    - User Story: US-034 Polyphonic Voice Mixer En Triads
    - User Story: US-035 Sustained Note Audio Engine
    - User Story: US-036 MIDI Pitch Bend Mapping En DSP
    - User Story: US-037 MIDI Modulation CC1 Mapping En DSP
    - User Story: US-038 Performance Mode Until Interrupt
    - User Story: US-039 Sustain Pedal CC64
    - User Story: US-040 Envelope Release / Soft Note-Off
    - User Story: US-041 Amp Envelope ADSR Parameters
    - User Story: US-042 MIDI Performance Patch YAML Config
    - Version: 0.1.0
    """

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
        list_devices.add_argument("--midi-device")
        list_devices.add_argument("--midi-device-id")
        list_devices.add_argument("--config")
        list_devices.set_defaults(handler=self._handle_midi_list_devices)
        virtual_input = midi_subparsers.add_parser(
            "diagnose-virtual-input",
            help="Diagnose whether virtual MIDI input prerequisites are present.",
        )
        virtual_input.set_defaults(handler=self._handle_midi_diagnose_virtual_input)
        virtual_port = midi_subparsers.add_parser(
            "virtual-port",
            help="Open a bounded virtual MIDI input port for Logic/DAW visibility tests.",
        )
        virtual_port.add_argument("--name", default="python-d1-synth")
        virtual_port.add_argument("--timeout", type=float, default=60.0)
        virtual_port.add_argument("--debuglevel", choices=[item.value for item in DebugLevel], default=DebugLevel.NONE.value)
        virtual_port.set_defaults(handler=self._handle_midi_virtual_port)
        usb_input = midi_subparsers.add_parser(
            "diagnose-usb-input",
            help="Diagnose whether a generic USB MIDI input device is visible.",
        )
        usb_input.add_argument("--midi-device")
        usb_input.add_argument("--midi-device-id")
        usb_input.add_argument("--config")
        usb_input.add_argument("--unsafe-rtmidi-scan", action="store_true")
        usb_input.set_defaults(handler=self._handle_midi_diagnose_usb_input)
        listen = midi_subparsers.add_parser(
            "listen",
            help="Listen to a selected MIDI input for a bounded number of note messages.",
        )
        listen.add_argument("--midi-device")
        listen.add_argument("--midi-device-id")
        listen.add_argument("--config")
        listen.add_argument("--unsafe-rtmidi-scan", action="store_true")
        listen.add_argument("--max-messages", type=int, default=10)
        listen.add_argument("--timeout", type=float, default=5.0)
        listen.add_argument("--debuglevel", choices=[item.value for item in DebugLevel], default=DebugLevel.NONE.value)
        listen.set_defaults(handler=self._handle_midi_listen)
        play_live = midi_subparsers.add_parser(
            "play-live",
            help="Listen to a selected MIDI input and play received note events through the synth engine.",
        )
        play_live.add_argument("--midi-device")
        play_live.add_argument("--midi-device-id")
        play_live.add_argument("--config")
        play_live.add_argument("--unsafe-rtmidi-scan", action="store_true")
        play_live.add_argument("--max-messages", type=int, default=10)
        play_live.add_argument("--timeout", type=float, default=5.0)
        play_live.add_argument("--waveform", choices=[item.value for item in Waveform], default=Waveform.SINE.value)
        play_live.add_argument("--sample-rate", type=int, default=44100)
        play_live.add_argument("--channel", choices=[item.value for item in OutputChannel], default=OutputChannel.STEREO.value)
        play_live.add_argument("--audio-device")
        play_live.add_argument("--debuglevel", choices=[item.value for item in DebugLevel], default=DebugLevel.NONE.value)
        play_live.set_defaults(handler=self._handle_midi_play_live)
        play_virtual = midi_subparsers.add_parser(
            "play-virtual",
            help="Open a virtual MIDI input port and play received Logic/DAW notes through the synth engine.",
        )
        play_virtual.add_argument("--port-name", "--name", dest="port_name", default="python-d1-synth")
        play_virtual.add_argument("--max-messages", type=int, default=10)
        play_virtual.add_argument("--timeout", type=float, default=30.0)
        play_virtual.add_argument("--waveform", choices=[item.value for item in Waveform], default=Waveform.SINE.value)
        play_virtual.add_argument("--sample-rate", type=int, default=44100)
        play_virtual.add_argument("--channel", choices=[item.value for item in OutputChannel], default=OutputChannel.STEREO.value)
        play_virtual.add_argument("--audio-device")
        play_virtual.add_argument("--debuglevel", choices=[item.value for item in DebugLevel], default=DebugLevel.NONE.value)
        play_virtual.set_defaults(handler=self._handle_midi_play_virtual)
        play_stream = midi_subparsers.add_parser(
            "play-stream",
            help="Open a virtual MIDI input port and stream note_on events through short audio buffers.",
        )
        play_stream.add_argument("--config")
        play_stream.add_argument("--port-name", "--name", dest="port_name")
        play_stream.add_argument("--max-messages", type=int)
        play_stream.add_argument("--timeout", type=float)
        play_stream.add_argument("--poll-interval", type=float)
        play_stream.add_argument("--note-duration", type=float)
        play_stream.add_argument(
            "--voice-mode",
            choices=[item.value for item in StreamingVoiceMode],
        )
        play_stream.add_argument("--dedupe-window", type=float)
        play_stream.add_argument("--chord-window", type=float)
        play_stream.add_argument("--pitch-bend-range", type=float)
        play_stream.add_argument(
            "--pitch-bend-channel-mode",
            choices=[item.value for item in PitchBendChannelMode],
        )
        play_stream.add_argument("--max-control-messages", type=int)
        play_stream.add_argument("--modulation-vibrato-depth", type=float)
        play_stream.add_argument("--modulation-vibrato-rate", type=float)
        play_stream.add_argument("--until-interrupt", action="store_true")
        play_stream.add_argument("--attack-time", type=float)
        play_stream.add_argument("--decay-time", type=float)
        play_stream.add_argument("--sustain-level", type=float)
        play_stream.add_argument("--release-time", type=float)
        play_stream.add_argument("--waveform", choices=[item.value for item in Waveform])
        play_stream.add_argument("--sample-rate", type=int)
        play_stream.add_argument("--channel", choices=[item.value for item in OutputChannel])
        play_stream.add_argument("--audio-device")
        play_stream.add_argument("--debuglevel", choices=[item.value for item in DebugLevel])
        play_stream.set_defaults(handler=self._handle_midi_play_stream)

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
        reporter.verbose(f"Output channel: {args.channel}")
        reporter.verbose(
            "Playback settings: "
            f"waveform={args.waveform}, duration={args.duration:g}s, "
            f"sample_rate={args.sample_rate} Hz, channel={args.channel}"
        )

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
            self._report_midi_scan_details(reporter, result)
            if result.error_message is not None:
                reporter.light(result.error_message)
                reporter.light(
                    "If Logic Pro shows devices but Python does not, record the Logic/Audio MIDI Setup device "
                    "list and treat this as a Python MIDI backend scan issue."
                )
                reporter.light("BLOCKER: Logic Pro shows MIDI devices but Python scan returned none.")
            reporter.light("No MIDI devices detected or optional MIDI backend is not installed.")
            print("No MIDI devices found.")
            return 0
        for device in devices:
            print(f"{device.identifier}\t{device.direction}\t{device.name}")
        config_device = self._load_midi_default_device(args.config)
        selection = MidiDeviceSelector().select_input_device(
            devices,
            cli_device=args.midi_device,
            cli_device_id=args.midi_device_id,
            config_device=config_device,
        )
        if selection.message and selection.source != "none":
            reporter.light(selection.message)
        return 0

    def _handle_midi_diagnose_virtual_input(self, args: argparse.Namespace) -> int:
        backend_available = importlib.util.find_spec("mido") is not None
        diagnostic = VirtualMidiInputAdapter().diagnose(backend_available=backend_available)
        print(diagnostic.message)
        return 0

    def _handle_midi_virtual_port(self, args: argparse.Namespace) -> int:
        reporter = DebugReporter(DebugLevel(args.debuglevel))
        try:
            settings = VirtualMidiPortSettings(port_name=args.name, timeout_seconds=args.timeout)
        except ValueError as exc:
            print(f"Virtual MIDI port error: {exc}", file=sys.stderr)
            return 2
        reporter.light(f"Opening virtual MIDI input port: {settings.port_name}")
        reporter.light(
            "Keep this command running while you check Logic Pro or another DAW for the virtual MIDI destination."
        )
        try:
            result = VirtualMidiPortManager().open(settings)
        except RuntimeError as exc:
            print(f"Virtual MIDI port error: {exc}", file=sys.stderr)
            return 2
        print(result.message)
        return 0

    def _handle_midi_diagnose_usb_input(self, args: argparse.Namespace) -> int:
        result = MidiDeviceScanner(allow_unsafe_native_scan=args.unsafe_rtmidi_scan).scan()
        config_device = self._load_midi_default_device(args.config)
        selection = MidiDeviceSelector().select_input_device(
            result.devices,
            cli_device=args.midi_device,
            cli_device_id=args.midi_device_id,
            config_device=config_device,
        )
        requested_device = None
        if selection.matched_device is not None:
            requested_device = selection.matched_device.identifier
        elif selection.source != "none":
            requested_device = selection.selected_device
        diagnostic = UsbMidiHardwareInputAdapter().diagnose(result.devices, requested_device=requested_device)
        if result.error_message is not None:
            self._print_midi_scan_details(result)
            print(result.error_message)
            print("First run: python -m synth midi list-devices --unsafe-rtmidi-scan")
            print(
                "If Logic Pro shows devices but Python does not, record the Logic/Audio MIDI Setup device list "
                "and choose a visible device for the manual test."
            )
            print("BLOCKER: Logic Pro shows MIDI devices but Python scan returned none.")
        if selection.message and selection.source != "none":
            print(selection.message)
        print(diagnostic.message)
        if diagnostic.compatible_devices:
            print("Compatible USB MIDI inputs:")
            for device in diagnostic.compatible_devices:
                print(f"{device.identifier}\t{device.name}")
        return 0

    def _handle_midi_listen(self, args: argparse.Namespace) -> int:
        reporter = DebugReporter(DebugLevel(args.debuglevel))
        result = MidiDeviceScanner(allow_unsafe_native_scan=args.unsafe_rtmidi_scan).scan()
        devices = result.devices
        if not devices:
            self._report_midi_scan_details(reporter, result)
            if result.error_message is not None:
                reporter.light(result.error_message)
            print("No MIDI input devices found. Run midi list-devices before midi listen.")
            return 0

        config_device = self._load_midi_default_device(args.config)
        selection = MidiDeviceSelector().select_input_device(
            devices,
            cli_device=args.midi_device,
            cli_device_id=args.midi_device_id,
            config_device=config_device,
        )
        if selection.message:
            reporter.light(selection.message)
        if selection.matched_device is None:
            return 0

        settings = MidiInputReceiveSettings(
            input_name=selection.matched_device.name,
            max_messages=args.max_messages,
            timeout_seconds=args.timeout,
        )
        try:
            result = LiveMidiInputReceiver().receive(settings)
        except RuntimeError as exc:
            print(f"MIDI listen error: {exc}", file=sys.stderr)
            return 2

        print(result.message)
        if result.note_sequence.events:
            print(f"Received sequence: {self._format_sequence_events(result.note_sequence)}")
        return 0

    def _handle_midi_play_live(self, args: argparse.Namespace) -> int:
        reporter = DebugReporter(DebugLevel(args.debuglevel))
        result = MidiDeviceScanner(allow_unsafe_native_scan=args.unsafe_rtmidi_scan).scan()
        devices = result.devices
        if not devices:
            self._report_midi_scan_details(reporter, result)
            if result.error_message is not None:
                reporter.light(result.error_message)
            print("No MIDI input devices found. Run midi list-devices before midi play-live.")
            return 0

        config_device = self._load_midi_default_device(args.config)
        selection = MidiDeviceSelector().select_input_device(
            devices,
            cli_device=args.midi_device,
            cli_device_id=args.midi_device_id,
            config_device=config_device,
        )
        if selection.message:
            reporter.light(selection.message)
        if selection.matched_device is None:
            return 0

        audio_selection = AudioDeviceSelector().select(args.audio_device)
        if audio_selection.sounddevice_value is not None:
            reporter.light(f"Selected audio device from {audio_selection.source}: {audio_selection.sounddevice_value}")

        settings = MidiAudioTriggerSettings(
            input_name=selection.matched_device.name,
            max_messages=args.max_messages,
            timeout_seconds=args.timeout,
            sample_rate=args.sample_rate,
            waveform=Waveform(args.waveform),
            channel=OutputChannel(args.channel),
            audio_device=audio_selection.sounddevice_value,
        )
        reporter.verbose(
            "MIDI audio trigger settings: "
            f"waveform={args.waveform}, sample_rate={args.sample_rate} Hz, channel={args.channel}"
        )
        try:
            result = MidiAudioTrigger().trigger(settings)
        except RuntimeError as exc:
            print(f"MIDI audio trigger error: {exc}", file=sys.stderr)
            return 2

        print(result.message)
        reporter.verbose(f"Audio buffer: {result.audio_frame_count} frames, {result.sample_rate} Hz")
        return 0

    def _handle_midi_play_virtual(self, args: argparse.Namespace) -> int:
        reporter = DebugReporter(DebugLevel(args.debuglevel))
        audio_selection = AudioDeviceSelector().select(args.audio_device)
        if audio_selection.sounddevice_value is not None:
            reporter.light(f"Selected audio device from {audio_selection.source}: {audio_selection.sounddevice_value}")
        try:
            settings = VirtualMidiAudioTriggerSettings(
                port_name=args.port_name,
                max_messages=args.max_messages,
                timeout_seconds=args.timeout,
                sample_rate=args.sample_rate,
                waveform=Waveform(args.waveform),
                channel=OutputChannel(args.channel),
                audio_device=audio_selection.sounddevice_value,
            )
        except ValueError as exc:
            print(f"Virtual MIDI audio trigger error: {exc}", file=sys.stderr)
            return 2

        reporter.light(f"Opening virtual MIDI input port: {settings.port_name}")
        reporter.light(
            "Keep this command running while Logic Pro or another DAW sends notes to this MIDI destination."
        )
        reporter.light(
            "MVP note: audio is rendered after --max-messages is reached or --timeout expires; "
            "use --max-messages 2 --timeout 10 for a quick Logic test."
        )
        reporter.verbose(
            "Virtual MIDI audio trigger settings: "
            f"port={settings.port_name}, max_messages={settings.max_messages}, "
            f"timeout={settings.timeout_seconds:g}s, waveform={args.waveform}, "
            f"sample_rate={args.sample_rate} Hz, channel={args.channel}"
        )
        original_sigint_handler = signal.getsignal(signal.SIGINT)

        def _raise_keyboard_interrupt(signum, frame) -> None:
            raise KeyboardInterrupt

        try:
            signal.signal(signal.SIGINT, _raise_keyboard_interrupt)
            result = VirtualMidiAudioTrigger().trigger(settings)
        except KeyboardInterrupt:
            print("Virtual MIDI audio trigger interrupted by user.", file=sys.stderr)
            return 130
        except RuntimeError as exc:
            print(f"Virtual MIDI audio trigger error: {exc}", file=sys.stderr)
            return 2
        finally:
            signal.signal(signal.SIGINT, original_sigint_handler)

        print(result.message)
        if result.received_messages:
            reporter.verbose(f"Received MIDI messages: {self._format_midi_messages(result.received_messages)}")
        if result.played_events:
            reporter.verbose(f"Rendered sequence events: {self._format_sequence_events(NoteSequence(result.played_events))}")
        reporter.verbose(f"Audio buffer: {result.audio_frame_count} frames, {result.sample_rate} Hz")
        return 0

    def _handle_midi_play_stream(self, args: argparse.Namespace) -> int:
        patch_config = self._load_patch_config(args.config)
        performance_config = patch_config.midi.performance if patch_config is not None else MidiPerformanceConfig()
        debuglevel = self._config_value(
            args.debuglevel,
            patch_config.debuglevel.value if patch_config is not None else None,
            DebugLevel.NONE.value,
        )
        reporter = DebugReporter(DebugLevel(debuglevel))
        audio_device = self._config_value(args.audio_device, performance_config.audio_device, None)
        audio_selection = AudioDeviceSelector().select(audio_device)
        if audio_selection.sounddevice_value is not None:
            reporter.light(f"Selected audio device from {audio_selection.source}: {audio_selection.sounddevice_value}")
        try:
            settings = StreamingMidiAudioTriggerSettings(
                port_name=self._config_value(args.port_name, performance_config.port_name, "python-d1-synth"),
                max_messages=self._config_value(args.max_messages, performance_config.max_messages, 32),
                timeout_seconds=self._config_value(args.timeout, performance_config.timeout_seconds, 30.0),
                poll_interval_seconds=self._config_value(
                    args.poll_interval,
                    performance_config.poll_interval_seconds,
                    0.005,
                ),
                note_duration_seconds=self._config_value(
                    args.note_duration,
                    performance_config.note_duration_seconds,
                    0.25,
                ),
                voice_mode=StreamingVoiceMode(
                    self._config_value(args.voice_mode, performance_config.voice_mode, StreamingVoiceMode.FIXED.value)
                ),
                dedupe_window_seconds=self._config_value(
                    args.dedupe_window,
                    performance_config.dedupe_window_seconds,
                    0.03,
                ),
                chord_window_seconds=self._config_value(args.chord_window, performance_config.chord_window_seconds, 0.02),
                pitch_bend_range_semitones=self._config_value(
                    args.pitch_bend_range,
                    performance_config.pitch_bend_range_semitones,
                    2.0,
                ),
                pitch_bend_channel_mode=PitchBendChannelMode(
                    self._config_value(
                        args.pitch_bend_channel_mode,
                        performance_config.pitch_bend_channel_mode,
                        PitchBendChannelMode.SAME.value,
                    )
                ),
                max_control_messages=self._config_value(
                    args.max_control_messages,
                    performance_config.max_control_messages,
                    1024,
                ),
                modulation_vibrato_depth_semitones=self._config_value(
                    args.modulation_vibrato_depth,
                    performance_config.modulation_vibrato_depth_semitones,
                    0.25,
                ),
                modulation_vibrato_rate_hz=self._config_value(
                    args.modulation_vibrato_rate,
                    performance_config.modulation_vibrato_rate_hz,
                    5.0,
                ),
                run_until_interrupted=args.until_interrupt
                or self._config_value(None, performance_config.run_until_interrupted, False),
                attack_time_seconds=self._config_value(args.attack_time, performance_config.attack_time_seconds, 0.0),
                decay_time_seconds=self._config_value(args.decay_time, performance_config.decay_time_seconds, 0.0),
                sustain_level=self._config_value(args.sustain_level, performance_config.sustain_level, 1.0),
                release_time_seconds=self._config_value(args.release_time, performance_config.release_time_seconds, 0.03),
                sample_rate=self._config_value(args.sample_rate, performance_config.sample_rate, 44100),
                waveform=Waveform(self._config_value(args.waveform, performance_config.waveform, Waveform.SINE.value)),
                amplitude=self._config_value(None, performance_config.amplitude, 0.2),
                channel=OutputChannel(
                    self._config_value(args.channel, performance_config.channel, OutputChannel.STEREO.value)
                ),
                audio_device=audio_selection.sounddevice_value,
            )
        except ValueError as exc:
            print(f"Streaming MIDI audio trigger error: {exc}", file=sys.stderr)
            return 2

        reporter.light(f"Opening streaming virtual MIDI input port: {settings.port_name}")
        if settings.run_until_interrupted:
            reporter.light("Performance mode: running until Ctrl-C; --max-messages and --timeout are ignored.")
        if settings.voice_mode is StreamingVoiceMode.SUSTAINED:
            reporter.light(
                "Sustained MVP note: note_on starts a streaming voice and note_off stops it; "
                "pitch bend bends active sustained voices; CC1 modulation adds vibrato; "
                "CC64 sustain pedal holds released voices; ADSR envelope shapes amplitude."
            )
        elif settings.voice_mode is StreamingVoiceMode.GATED:
            reporter.light(
                "Gated MVP note: note_on plays an audible fallback buffer and note_off reports duration; "
                "polyphonic chord batches are mixed, pitch bend and modulation are later stories."
            )
        else:
            reporter.light(
                "Near-realtime MVP note: note_on events are played as short fixed-duration audio buffers; "
                "polyphonic chord batches are mixed, note_off sustain, pitch bend and modulation are later stories."
            )
        reporter.verbose(
            "Streaming MIDI audio trigger settings: "
            f"port={settings.port_name}, max_messages={settings.max_messages}, "
            f"timeout={settings.timeout_seconds:g}s, poll_interval={settings.poll_interval_seconds:g}s, "
            f"note_duration={settings.note_duration_seconds:g}s, voice_mode={settings.voice_mode.value}, "
            f"dedupe_window={settings.dedupe_window_seconds:g}s, chord_window={settings.chord_window_seconds:g}s, "
            f"pitch_bend_range={settings.pitch_bend_range_semitones:g}st, "
            f"pitch_bend_channel_mode={settings.pitch_bend_channel_mode.value}, "
            f"max_control_messages={settings.max_control_messages}, "
            f"modulation_vibrato_depth={settings.modulation_vibrato_depth_semitones:g}st, "
            f"modulation_vibrato_rate={settings.modulation_vibrato_rate_hz:g}Hz, "
            f"until_interrupt={str(settings.run_until_interrupted).lower()}, "
            f"attack_time={settings.attack_time_seconds:g}s, "
            f"decay_time={settings.decay_time_seconds:g}s, "
            f"sustain_level={settings.sustain_level:g}, "
            f"release_time={settings.release_time_seconds:g}s, "
            f"waveform={settings.waveform.value}, "
            f"sample_rate={settings.sample_rate} Hz, channel={settings.channel.value}"
        )
        original_sigint_handler = signal.getsignal(signal.SIGINT)

        def _raise_keyboard_interrupt(signum, frame) -> None:
            raise KeyboardInterrupt

        try:
            signal.signal(signal.SIGINT, _raise_keyboard_interrupt)
            signal.siginterrupt(signal.SIGINT, True)
            result = StreamingMidiAudioTrigger().trigger(settings)
        except KeyboardInterrupt:
            print("Streaming MIDI audio trigger interrupted by user.", file=sys.stderr)
            return 130
        except RuntimeError as exc:
            print(f"Streaming MIDI audio trigger error: {exc}", file=sys.stderr)
            return 2
        finally:
            signal.signal(signal.SIGINT, original_sigint_handler)

        print(result.message)
        if result.received_messages:
            reporter.verbose(f"Received MIDI messages: {self._format_midi_messages(result.received_messages)}")
        if result.played_events:
            reporter.verbose(f"Streamed sequence events: {self._format_sequence_events(NoteSequence(result.played_events))}")
            reporter.verbose(f"Streamed note durations: {self._format_note_event_durations(result.played_events)}")
        reporter.verbose(f"Suppressed duplicate MIDI messages: {result.suppressed_duplicate_count}")
        reporter.verbose(f"Total streamed audio frames: {result.audio_frame_count}, sample_rate={result.sample_rate} Hz")
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

    def _format_midi_messages(self, messages) -> str:
        formatted_messages = []
        for message in messages:
            if message.message_type == "pitch_bend":
                formatted_messages.append(
                    f"pitch_bend:{message.pitch_bend_value}:channel={message.channel}"
                )
                continue
            if message.message_type == "control_change":
                formatted_messages.append(
                    f"control_change:{message.control_number}:{message.control_value}:channel={message.channel}"
                )
                continue
            formatted_messages.append(
                f"{message.message_type}:{message.note_number}:velocity={message.velocity}:channel={message.channel}"
            )
        return ", ".join(formatted_messages)

    def _format_note_event_durations(self, events) -> str:
        return ", ".join(
            f"{event.note.name}{event.note.octave}@{event.start_seconds:.3f}s/{event.duration_seconds:.3f}s"
            for event in events
        )

    def _report_midi_scan_details(self, reporter: DebugReporter, result) -> None:
        backend_name = getattr(result, "backend_name", None)
        returncode = getattr(result, "returncode", None)
        stderr = getattr(result, "stderr", "")
        stdout = getattr(result, "stdout", "")
        if backend_name:
            reporter.light(f"MIDI backend: {backend_name}")
        if returncode is not None:
            reporter.light(f"MIDI backend return code: {returncode}")
        if stderr:
            reporter.light(f"MIDI backend stderr: {self._first_line(stderr)}")
        elif stdout:
            reporter.verbose(f"MIDI backend stdout: {self._first_line(stdout)}")

    def _print_midi_scan_details(self, result) -> None:
        backend_name = getattr(result, "backend_name", None)
        returncode = getattr(result, "returncode", None)
        stderr = getattr(result, "stderr", "")
        stdout = getattr(result, "stdout", "")
        if backend_name:
            print(f"MIDI backend: {backend_name}")
        if returncode is not None:
            print(f"MIDI backend return code: {returncode}")
        if stderr:
            print(f"MIDI backend stderr: {self._first_line(stderr)}")
        elif stdout:
            print(f"MIDI backend stdout: {self._first_line(stdout)}")

    def _first_line(self, value: str) -> str:
        lines = [line for line in value.splitlines() if line.strip()]
        if not lines:
            return ""
        if lines[0].startswith("Traceback") and len(lines) > 1:
            return lines[-1]
        return lines[0]

    def _load_midi_default_device(self, config_path: str | None) -> str | None:
        config = self._load_patch_config(config_path)
        if config is None:
            return None
        return config.midi.default_input_device

    def _load_patch_config(self, config_path: str | None) -> PatchConfig | None:
        if config_path is None:
            return None
        return PatchConfigLoader().load(Path(config_path))

    def _config_value(self, cli_value, config_value, default_value):
        if cli_value is not None:
            return cli_value
        if config_value is not None:
            return config_value
        return default_value


def main(argv: list[str] | None = None) -> int:
    return SynthCli().run(argv)
