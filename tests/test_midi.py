# Bestand: test_midi.py
# Versienummer: 0.1.0
# Doel: Unit tests voor MIDI discovery, selectie, virtual MIDI audio trigger en MIDI-naar-NoteEvent mapping.
# Sprint: Future MIDI/DAW
# User-Story: US-035 Sustained Note Audio Engine
# Actie: US-035-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-035

import pytest

from synth.audio import OutputChannel
from synth.midi import (
    DuplicateMidiEventGuard,
    DuplicateMidiEventGuardSettings,
    MidiAudioTrigger,
    MidiAudioTriggerResult,
    MidiAudioTriggerSettings,
    LiveMidiInputReceiver,
    MidiDevice,
    MidiDeviceScanner,
    MidiDeviceSelector,
    MidiInputReceiveSettings,
    MidiMessage,
    MidiMessageNormalizer,
    MidiToNoteEventMapper,
    StreamingMidiAudioTrigger,
    StreamingMidiAudioTriggerResult,
    StreamingMidiAudioTriggerSettings,
    StreamingVoiceMode,
    UsbMidiHardwareInputAdapter,
    VirtualMidiAudioTrigger,
    VirtualMidiAudioTriggerResult,
    VirtualMidiAudioTriggerSettings,
    VirtualMidiInputAdapter,
    VirtualMidiPortManager,
    VirtualMidiPortResult,
    VirtualMidiPortSettings,
)
from synth.notes import NoteEvent, NoteParser


class TestMidiDeviceSelector:
    def test_cli_device_wins_over_config_default(self) -> None:
        selection = MidiDeviceSelector().select("CLI Device", "Config Device")

        assert selection.selected_device == "CLI Device"
        assert selection.source == "cli"

    def test_config_default_used_without_cli_device(self) -> None:
        selection = MidiDeviceSelector().select(None, "Config Device")

        assert selection.selected_device == "Config Device"
        assert selection.source == "config"

    def test_cli_device_id_wins_over_name_and_config_default(self) -> None:
        devices = (
            MidiDevice(identifier="input:0", name="Keyboard", direction="input"),
            MidiDevice(identifier="input:1", name="Guitar MIDI", direction="input"),
        )

        selection = MidiDeviceSelector().select_input_device(
            devices,
            cli_device="Keyboard",
            cli_device_id="input:1",
            config_device="Config Default",
        )

        assert selection.selected_device == "input:1"
        assert selection.source == "cli-id"
        assert selection.matched_device == devices[1]
        assert selection.message == "Selected MIDI input device from cli-id: input:1 Guitar MIDI"

    def test_cli_device_name_wins_over_config_default(self) -> None:
        devices = (
            MidiDevice(identifier="input:0", name="Config Default", direction="input"),
            MidiDevice(identifier="input:1", name="Keyboard", direction="input"),
        )

        selection = MidiDeviceSelector().select_input_device(
            devices,
            cli_device="Keyboard",
            config_device="Config Default",
        )

        assert selection.selected_device == "Keyboard"
        assert selection.source == "cli"
        assert selection.matched_device == devices[1]

    def test_config_default_selects_input_device_without_cli_override(self) -> None:
        devices = (
            MidiDevice(identifier="input:0", name="Config Default", direction="input"),
            MidiDevice(identifier="output:0", name="Config Default Output", direction="output"),
        )

        selection = MidiDeviceSelector().select_input_device(devices, config_device="Config Default")

        assert selection.selected_device == "Config Default"
        assert selection.source == "config"
        assert selection.matched_device == devices[0]

    def test_missing_requested_input_device_returns_clear_message(self) -> None:
        devices = (MidiDevice(identifier="input:0", name="Keyboard", direction="input"),)

        selection = MidiDeviceSelector().select_input_device(devices, cli_device="Missing")

        assert selection.matched_device is None
        assert selection.source == "cli"
        assert "Requested MIDI input device not found" in selection.message
        assert "Keyboard" in selection.message
        assert "midi list-devices" in selection.message


class TestMidiDeviceScanner:
    def test_default_scanner_returns_safely_without_native_scan(self) -> None:
        result = MidiDeviceScanner().scan()

        assert result.devices == tuple()
        assert result.error_message is None or isinstance(result.error_message, str)


class TestVirtualMidiInputAdapter:
    def test_note_on_and_note_off_messages_map_to_note_sequence(self) -> None:
        messages = (
            MidiMessage(message_type="note_on", note_number=60, velocity=96, channel=1, time_seconds=0.25),
            MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.75),
        )

        sequence = VirtualMidiInputAdapter().messages_to_note_sequence(messages)

        assert len(sequence.events) == 1
        event = sequence.events[0]
        assert event.note.name == "C"
        assert event.note.octave == 4
        assert event.duration_seconds == 0.5
        assert event.velocity == 96 / 127
        assert event.start_seconds == 0.25

    def test_note_on_with_zero_velocity_is_treated_as_note_off(self) -> None:
        messages = (
            MidiMessage(message_type="note_on", note_number=64, velocity=80, channel=1, time_seconds=1.0),
            MidiMessage(message_type="note_on", note_number=64, velocity=0, channel=1, time_seconds=1.25),
        )

        sequence = VirtualMidiInputAdapter().messages_to_note_sequence(messages)

        assert len(sequence.events) == 1
        event = sequence.events[0]
        assert event.note.name == "E"
        assert event.note.octave == 4
        assert event.duration_seconds == 0.25

    def test_unavailable_virtual_route_returns_clear_diagnostic(self) -> None:
        diagnostic = VirtualMidiInputAdapter().diagnose(backend_available=False)

        assert diagnostic.available is False
        assert "Virtual MIDI input backend is not available" in diagnostic.message


class TestMidiToNoteEventMapper:
    def test_note_on_and_note_off_map_to_note_event(self) -> None:
        messages = (
            MidiMessage(message_type="note_on", note_number=60, velocity=64, channel=1, time_seconds=0.1),
            MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.6),
        )

        sequence = MidiToNoteEventMapper().messages_to_note_sequence(messages)

        event = sequence.events[0]
        assert event.note.name == "C"
        assert event.note.octave == 4
        assert event.duration_seconds == 0.5
        assert event.velocity == 64 / 127
        assert event.start_seconds == 0.1

    def test_note_on_with_velocity_zero_closes_active_note(self) -> None:
        messages = (
            MidiMessage(message_type="note_on", note_number=67, velocity=100, channel=1, time_seconds=1.0),
            MidiMessage(message_type="note_on", note_number=67, velocity=0, channel=1, time_seconds=1.4),
        )

        sequence = MidiToNoteEventMapper().messages_to_note_sequence(messages)

        event = sequence.events[0]
        assert event.note.name == "G"
        assert event.note.octave == 4
        assert event.duration_seconds == pytest.approx(0.4)

    def test_missing_note_off_uses_default_duration(self) -> None:
        messages = (MidiMessage(message_type="note_on", note_number=69, velocity=127, channel=1, time_seconds=2.0),)

        sequence = MidiToNoteEventMapper(default_note_duration_seconds=0.75).messages_to_note_sequence(messages)

        event = sequence.events[0]
        assert event.note.name == "A"
        assert event.note.octave == 4
        assert event.duration_seconds == 0.75

    def test_same_note_on_different_channels_maps_independently(self) -> None:
        messages = (
            MidiMessage(message_type="note_on", note_number=60, velocity=90, channel=1, time_seconds=0.0),
            MidiMessage(message_type="note_on", note_number=60, velocity=45, channel=2, time_seconds=0.1),
            MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.5),
            MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=2, time_seconds=0.6),
        )

        sequence = MidiToNoteEventMapper().messages_to_note_sequence(messages)

        assert len(sequence.events) == 2
        assert sequence.events[0].start_seconds == 0.0
        assert sequence.events[0].duration_seconds == 0.5
        assert sequence.events[0].velocity == 90 / 127
        assert sequence.events[1].start_seconds == 0.1
        assert sequence.events[1].duration_seconds == 0.5
        assert sequence.events[1].velocity == 45 / 127

    def test_logic_region_multiple_note_pairs_map_to_multiple_ordered_events(self) -> None:
        messages = (
            MidiMessage(message_type="note_on", note_number=60, velocity=80, channel=1, time_seconds=0.00),
            MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.20),
            MidiMessage(message_type="note_on", note_number=62, velocity=82, channel=1, time_seconds=0.25),
            MidiMessage(message_type="note_off", note_number=62, velocity=0, channel=1, time_seconds=0.45),
            MidiMessage(message_type="note_on", note_number=64, velocity=84, channel=1, time_seconds=0.50),
            MidiMessage(message_type="note_off", note_number=64, velocity=0, channel=1, time_seconds=0.70),
        )

        sequence = MidiToNoteEventMapper().messages_to_note_sequence(messages)

        assert [f"{event.note.name}{event.note.octave}" for event in sequence.events] == ["C4", "D4", "E4"]
        assert [event.start_seconds for event in sequence.events] == [0.0, 0.25, 0.5]
        assert [event.duration_seconds for event in sequence.events] == pytest.approx([0.2, 0.2, 0.2])


class TestMidiMessageNormalizer:
    def test_mido_note_on_normalizes_zero_based_channel_to_one_based(self) -> None:
        raw_message = type(
            "RawMidiMessage",
            (),
            {"type": "note_on", "note": 60, "velocity": 100, "channel": 0, "time": 0.125},
        )()

        message = MidiMessageNormalizer().normalize(raw_message)

        assert message == MidiMessage(
            message_type="note_on",
            note_number=60,
            velocity=100,
            channel=1,
            time_seconds=0.125,
        )

    def test_non_note_messages_are_ignored_for_us026(self) -> None:
        raw_message = type("RawMidiMessage", (), {"type": "clock", "time": 0.0})()

        assert MidiMessageNormalizer().normalize(raw_message) is None

    def test_zero_backend_time_uses_receive_loop_fallback_time_for_us030(self) -> None:
        raw_message = type(
            "RawMidiMessage",
            (),
            {"type": "note_on", "note": 62, "velocity": 90, "channel": 0, "time": 0.0},
        )()

        message = MidiMessageNormalizer().normalize(raw_message, fallback_time_seconds=0.375)

        assert message == MidiMessage(
            message_type="note_on",
            note_number=62,
            velocity=90,
            channel=1,
            time_seconds=0.375,
        )


class TestDuplicateMidiEventGuard:
    def test_identical_message_inside_window_is_suppressed(self) -> None:
        guard = DuplicateMidiEventGuard(DuplicateMidiEventGuardSettings(window_seconds=0.03))
        first = MidiMessage(message_type="note_on", note_number=65, velocity=83, channel=1, time_seconds=5.299)
        duplicate = MidiMessage(message_type="note_on", note_number=65, velocity=83, channel=1, time_seconds=5.299)

        assert guard.is_duplicate(first) is False
        assert guard.is_duplicate(duplicate) is True

    def test_different_notes_at_same_time_are_not_suppressed_for_future_chords(self) -> None:
        guard = DuplicateMidiEventGuard(DuplicateMidiEventGuardSettings(window_seconds=0.03))
        first = MidiMessage(message_type="note_on", note_number=60, velocity=80, channel=1, time_seconds=1.0)
        chord_tone = MidiMessage(message_type="note_on", note_number=64, velocity=80, channel=1, time_seconds=1.0)

        assert guard.is_duplicate(first) is False
        assert guard.is_duplicate(chord_tone) is False

    def test_same_message_after_window_is_not_suppressed(self) -> None:
        guard = DuplicateMidiEventGuard(DuplicateMidiEventGuardSettings(window_seconds=0.03))
        first = MidiMessage(message_type="note_on", note_number=60, velocity=80, channel=1, time_seconds=1.0)
        repeated_note = MidiMessage(message_type="note_on", note_number=60, velocity=80, channel=1, time_seconds=1.05)

        assert guard.is_duplicate(first) is False
        assert guard.is_duplicate(repeated_note) is False

    def test_settings_require_positive_window(self) -> None:
        with pytest.raises(ValueError, match="window_seconds"):
            DuplicateMidiEventGuardSettings(window_seconds=0)


class TestLiveMidiInputReceiver:
    def test_receive_loop_maps_fake_backend_messages_to_note_sequence(self) -> None:
        class FakeBackend:
            def receive_messages(self, input_name, max_messages, timeout_seconds):
                assert input_name == "Generic Keyboard"
                assert max_messages == 2
                assert timeout_seconds == 0.5
                return (
                    MidiMessage(message_type="note_on", note_number=60, velocity=90, channel=1, time_seconds=0.0),
                    MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.25),
                )

        settings = MidiInputReceiveSettings(input_name="Generic Keyboard", max_messages=2, timeout_seconds=0.5)

        result = LiveMidiInputReceiver(backend=FakeBackend()).receive(settings)

        assert result.received_messages[0].note_number == 60
        assert len(result.note_sequence.events) == 1
        assert result.note_sequence.events[0].note.name == "C"
        assert result.note_sequence.events[0].duration_seconds == 0.25
        assert result.message == "Received 2 MIDI note messages from Generic Keyboard."

    def test_receive_settings_require_selected_input_name(self) -> None:
        with pytest.raises(ValueError, match="input_name"):
            MidiInputReceiveSettings(input_name="")


class TestVirtualMidiPortManager:
    def test_open_uses_backend_with_selected_port_name_and_timeout(self) -> None:
        class FakeVirtualPortBackend:
            def open_virtual_input(self, port_name, timeout_seconds):
                assert port_name == "python-d1-synth"
                assert timeout_seconds == 0.5
                return VirtualMidiPortResult(
                    port_name=port_name,
                    opened=True,
                    message="Virtual MIDI input port opened: python-d1-synth.",
                )

        settings = VirtualMidiPortSettings(port_name="python-d1-synth", timeout_seconds=0.5)

        result = VirtualMidiPortManager(backend=FakeVirtualPortBackend()).open(settings)

        assert result.opened is True
        assert result.port_name == "python-d1-synth"
        assert result.message == "Virtual MIDI input port opened: python-d1-synth."

    def test_virtual_port_settings_require_non_empty_port_name(self) -> None:
        with pytest.raises(ValueError, match="port_name"):
            VirtualMidiPortSettings(port_name="")

    def test_virtual_port_settings_require_positive_timeout(self) -> None:
        with pytest.raises(ValueError, match="timeout_seconds"):
            VirtualMidiPortSettings(timeout_seconds=0)


class TestMidiAudioTrigger:
    def test_trigger_receives_midi_sequence_renders_audio_and_plays_selected_device(self) -> None:
        class FakeReceiver:
            def receive(self, settings):
                note = MidiToNoteEventMapper().messages_to_note_sequence(
                    (
                        MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=0.0),
                        MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.1),
                    )
                )
                return type(
                    "FakeReceiveResult",
                    (),
                    {
                        "input_name": settings.input_name,
                        "received_messages": (
                            MidiMessage(
                                message_type="note_on",
                                note_number=60,
                                velocity=100,
                                channel=1,
                                time_seconds=0.0,
                            ),
                            MidiMessage(
                                message_type="note_off",
                                note_number=60,
                                velocity=0,
                                channel=1,
                                time_seconds=0.1,
                            ),
                        ),
                        "note_sequence": note,
                        "message": "Received 2 MIDI note messages from Generic Keyboard.",
                    },
                )()

        class FakeAudioPlayer:
            def __init__(self):
                self.calls = []

            def play(self, buffer, device=None):
                self.calls.append((buffer.samples.shape, buffer.sample_rate, device))

        audio_player = FakeAudioPlayer()
        settings = MidiAudioTriggerSettings(
            input_name="Generic Keyboard",
            max_messages=2,
            timeout_seconds=0.5,
            sample_rate=44100,
            channel=OutputChannel.STEREO,
            audio_device="Scarlett 8i6 USB",
        )

        result = MidiAudioTrigger(receiver=FakeReceiver(), audio_player=audio_player).trigger(settings)

        assert result == MidiAudioTriggerResult(
            input_name="Generic Keyboard",
            received_message_count=2,
            played_event_count=1,
            audio_frame_count=4410,
            sample_rate=44100,
            message="Played 1 MIDI-triggered note events from Generic Keyboard.",
        )
        assert audio_player.calls == [((4410, 2), 44100, "Scarlett 8i6 USB")]

    def test_trigger_does_not_play_audio_when_no_note_events_are_received(self) -> None:
        class FakeReceiver:
            def receive(self, settings):
                return type(
                    "FakeReceiveResult",
                    (),
                    {
                        "input_name": settings.input_name,
                        "received_messages": tuple(),
                        "note_sequence": MidiToNoteEventMapper().messages_to_note_sequence(tuple()),
                        "message": "Received 0 MIDI note messages from Generic Keyboard.",
                    },
                )()

        class FakeAudioPlayer:
            def play(self, buffer, device=None):
                raise AssertionError("audio should not play without note events")

        settings = MidiAudioTriggerSettings(input_name="Generic Keyboard")

        result = MidiAudioTrigger(receiver=FakeReceiver(), audio_player=FakeAudioPlayer()).trigger(settings)

        assert result.played_event_count == 0
        assert result.audio_frame_count == 0
        assert result.message == "Received 0 MIDI-triggered note events from Generic Keyboard; no audio played."

    def test_trigger_settings_require_positive_values(self) -> None:
        with pytest.raises(ValueError, match="sample_rate"):
            MidiAudioTriggerSettings(input_name="Generic Keyboard", sample_rate=0)


class TestVirtualMidiAudioTrigger:
    def test_virtual_trigger_receives_daw_sequence_and_plays_audio(self) -> None:
        class FakeReceiver:
            def receive(self, settings):
                note_sequence = MidiToNoteEventMapper().messages_to_note_sequence(
                    (
                        MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=0.0),
                        MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.1),
                    )
                )
                return type(
                    "FakeReceiveResult",
                    (),
                    {
                        "input_name": settings.input_name,
                        "received_messages": (
                            MidiMessage(
                                message_type="note_on",
                                note_number=60,
                                velocity=100,
                                channel=1,
                                time_seconds=0.0,
                            ),
                            MidiMessage(
                                message_type="note_off",
                                note_number=60,
                                velocity=0,
                                channel=1,
                                time_seconds=0.1,
                            ),
                        ),
                        "note_sequence": note_sequence,
                        "message": "Received 2 MIDI note messages from python-d1-synth.",
                    },
                )()

        class FakeAudioPlayer:
            def __init__(self):
                self.calls = []

            def play(self, buffer, device=None):
                self.calls.append((buffer.samples.shape, buffer.sample_rate, device))

        audio_player = FakeAudioPlayer()
        settings = VirtualMidiAudioTriggerSettings(
            port_name="python-d1-synth",
            max_messages=2,
            timeout_seconds=0.5,
            sample_rate=44100,
            channel=OutputChannel.STEREO,
            audio_device="Scarlett 8i6 USB",
        )

        result = VirtualMidiAudioTrigger(receiver=FakeReceiver(), audio_player=audio_player).trigger(settings)
        expected_event = NoteEvent(
            note=NoteParser().parse("C4"),
            duration_seconds=0.1,
            velocity=100 / 127,
            start_seconds=0.0,
        )

        assert result == VirtualMidiAudioTriggerResult(
            port_name="python-d1-synth",
            received_message_count=2,
            played_event_count=1,
            audio_frame_count=4410,
            sample_rate=44100,
            message="Played 1 MIDI-triggered note events from virtual MIDI port python-d1-synth.",
            received_messages=(
                MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=0.0),
                MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.1),
            ),
            played_events=(expected_event,),
        )
        assert audio_player.calls == [((4410, 2), 44100, "Scarlett 8i6 USB")]
        assert [f"{event.note.name}{event.note.octave}" for event in result.played_events] == ["C4"]

    def test_virtual_trigger_renders_multiple_logic_region_notes(self) -> None:
        class FakeReceiver:
            def receive(self, settings):
                messages = (
                    MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=0.0),
                    MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.1),
                    MidiMessage(message_type="note_on", note_number=62, velocity=96, channel=1, time_seconds=0.2),
                    MidiMessage(message_type="note_off", note_number=62, velocity=0, channel=1, time_seconds=0.3),
                    MidiMessage(message_type="note_on", note_number=64, velocity=90, channel=1, time_seconds=0.4),
                    MidiMessage(message_type="note_off", note_number=64, velocity=0, channel=1, time_seconds=0.5),
                )
                return type(
                    "FakeReceiveResult",
                    (),
                    {
                        "input_name": settings.input_name,
                        "received_messages": messages,
                        "note_sequence": MidiToNoteEventMapper().messages_to_note_sequence(messages),
                        "message": "Received 6 MIDI note messages from python-d1-synth.",
                    },
                )()

        class FakeAudioPlayer:
            def __init__(self):
                self.calls = []

            def play(self, buffer, device=None):
                self.calls.append((buffer.samples.shape, buffer.sample_rate, device))

        audio_player = FakeAudioPlayer()
        settings = VirtualMidiAudioTriggerSettings(
            port_name="python-d1-synth",
            max_messages=6,
            timeout_seconds=1.0,
            sample_rate=44100,
            channel=OutputChannel.STEREO,
            audio_device="Scarlett 8i6 USB",
        )

        result = VirtualMidiAudioTrigger(receiver=FakeReceiver(), audio_player=audio_player).trigger(settings)

        assert result.received_message_count == 6
        assert result.played_event_count == 3
        assert result.audio_frame_count == 22050
        assert [f"{event.note.name}{event.note.octave}" for event in result.played_events] == ["C4", "D4", "E4"]
        assert [event.start_seconds for event in result.played_events] == [0.0, 0.2, 0.4]
        assert audio_player.calls == [((22050, 2), 44100, "Scarlett 8i6 USB")]

    def test_virtual_trigger_reports_zero_midi_messages_without_audio(self) -> None:
        class FakeReceiver:
            def receive(self, settings):
                return type(
                    "FakeReceiveResult",
                    (),
                    {
                        "input_name": settings.input_name,
                        "received_messages": tuple(),
                        "note_sequence": MidiToNoteEventMapper().messages_to_note_sequence(tuple()),
                        "message": "Received 0 MIDI note messages from python-d1-synth.",
                    },
                )()

        class FakeAudioPlayer:
            def play(self, buffer, device=None):
                raise AssertionError("audio should not play when the virtual port receives no MIDI")

        settings = VirtualMidiAudioTriggerSettings(port_name="python-d1-synth", max_messages=1, timeout_seconds=0.1)

        result = VirtualMidiAudioTrigger(receiver=FakeReceiver(), audio_player=FakeAudioPlayer()).trigger(settings)

        assert result == VirtualMidiAudioTriggerResult(
            port_name="python-d1-synth",
            received_message_count=0,
            played_event_count=0,
            audio_frame_count=0,
            sample_rate=44100,
            message="Received 0 MIDI note messages from virtual MIDI port python-d1-synth; no audio played.",
            received_messages=tuple(),
            played_events=tuple(),
        )

    def test_virtual_trigger_settings_require_non_empty_port_name(self) -> None:
        with pytest.raises(ValueError, match="port_name"):
            VirtualMidiAudioTriggerSettings(port_name="")


class TestStreamingMidiAudioTrigger:
    def test_streaming_trigger_plays_each_note_on_without_waiting_for_batch_end(self) -> None:
        class FakeStreamingBackend:
            def __init__(self):
                self.calls = []

            def iter_messages(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                self.calls.append((input_name, max_messages, timeout_seconds, poll_interval_seconds))
                yield MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=0.01)
                yield MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.08)
                yield MidiMessage(message_type="note_on", note_number=62, velocity=90, channel=1, time_seconds=0.12)

        class FakeAudioPlayer:
            def __init__(self):
                self.calls = []

            def play(self, buffer, device=None):
                self.calls.append((buffer.samples.shape, buffer.sample_rate, device))

        backend = FakeStreamingBackend()
        audio_player = FakeAudioPlayer()
        settings = StreamingMidiAudioTriggerSettings(
            port_name="python-d1-synth",
            max_messages=3,
            timeout_seconds=1.0,
            poll_interval_seconds=0.002,
            note_duration_seconds=0.25,
            sample_rate=44100,
            channel=OutputChannel.STEREO,
            audio_device="Scarlett 8i6 USB",
        )

        result = StreamingMidiAudioTrigger(backend=backend, audio_player=audio_player).trigger(settings)
        expected_events = (
            NoteEvent(note=NoteParser().parse("C4"), duration_seconds=0.25, velocity=100 / 127, start_seconds=0.01),
            NoteEvent(note=NoteParser().parse("D4"), duration_seconds=0.25, velocity=90 / 127, start_seconds=0.12),
        )

        assert backend.calls == [("python-d1-synth", 3, 1.0, 0.002)]
        assert result == StreamingMidiAudioTriggerResult(
            port_name="python-d1-synth",
            received_message_count=3,
            played_event_count=2,
            audio_frame_count=22050,
            sample_rate=44100,
            message=(
                "Streamed 2 MIDI-triggered note events from virtual MIDI port python-d1-synth; "
                "suppressed 0 duplicate MIDI messages."
            ),
            received_messages=(
                MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=0.01),
                MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.08),
                MidiMessage(message_type="note_on", note_number=62, velocity=90, channel=1, time_seconds=0.12),
            ),
            played_events=expected_events,
            suppressed_duplicate_count=0,
        )
        assert [f"{event.note.name}{event.note.octave}" for event in result.played_events] == ["C4", "D4"]
        assert [event.start_seconds for event in result.played_events] == [0.01, 0.12]
        assert audio_player.calls == [
            ((11025, 2), 44100, "Scarlett 8i6 USB"),
            ((11025, 2), 44100, "Scarlett 8i6 USB"),
        ]

    def test_streaming_trigger_suppresses_duplicate_logic_echoes_without_dropping_chord_tones(self) -> None:
        class FakeStreamingBackend:
            def iter_messages(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                yield MidiMessage(message_type="note_on", note_number=65, velocity=83, channel=1, time_seconds=5.299)
                yield MidiMessage(message_type="note_on", note_number=65, velocity=83, channel=1, time_seconds=5.299)
                yield MidiMessage(message_type="note_on", note_number=64, velocity=77, channel=1, time_seconds=5.299)
                yield MidiMessage(message_type="note_on", note_number=64, velocity=77, channel=1, time_seconds=5.299)
                yield MidiMessage(message_type="note_on", note_number=60, velocity=61, channel=1, time_seconds=5.299)
                yield MidiMessage(message_type="note_on", note_number=57, velocity=65, channel=1, time_seconds=5.299)

        class FakeAudioPlayer:
            def __init__(self):
                self.calls = []

            def play(self, buffer, device=None):
                self.calls.append((buffer.samples.shape, buffer.sample_rate, device))

        audio_player = FakeAudioPlayer()
        settings = StreamingMidiAudioTriggerSettings(
            port_name="python-d1-synth",
            max_messages=6,
            timeout_seconds=1.0,
            note_duration_seconds=0.25,
            dedupe_window_seconds=0.03,
        )

        result = StreamingMidiAudioTrigger(backend=FakeStreamingBackend(), audio_player=audio_player).trigger(settings)

        assert result.received_message_count == 6
        assert result.played_event_count == 4
        assert result.suppressed_duplicate_count == 2
        assert [f"{event.note.name}{event.note.octave}" for event in result.played_events] == ["F4", "E4", "C4", "A3"]
        assert len(audio_player.calls) == 4
        assert result.message == (
            "Streamed 4 MIDI-triggered note events from virtual MIDI port python-d1-synth; "
            "suppressed 2 duplicate MIDI messages."
        )

    def test_streaming_trigger_mixes_simultaneous_note_on_batch_as_one_triad_buffer(self) -> None:
        class FakeStreamingBatchBackend:
            def iter_messages(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                raise AssertionError("US-034 should prefer batch polling when available")

            def iter_message_batches(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                yield (
                    MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=1.0),
                    MidiMessage(message_type="note_on", note_number=64, velocity=96, channel=1, time_seconds=1.0),
                    MidiMessage(message_type="note_on", note_number=67, velocity=90, channel=1, time_seconds=1.0),
                )

        class FakeAudioPlayer:
            def __init__(self):
                self.calls = []

            def play(self, buffer, device=None):
                self.calls.append((buffer.samples.shape, buffer.sample_rate, device))

        audio_player = FakeAudioPlayer()
        settings = StreamingMidiAudioTriggerSettings(
            port_name="python-d1-synth",
            max_messages=3,
            timeout_seconds=1.0,
            note_duration_seconds=0.25,
            chord_window_seconds=0.02,
            audio_device="Scarlett 8i6 USB",
        )

        result = StreamingMidiAudioTrigger(backend=FakeStreamingBatchBackend(), audio_player=audio_player).trigger(
            settings
        )

        assert result.received_message_count == 3
        assert result.played_event_count == 3
        assert result.suppressed_duplicate_count == 0
        assert [f"{event.note.name}{event.note.octave}" for event in result.played_events] == ["C4", "E4", "G4"]
        assert audio_player.calls == [((11025, 2), 44100, "Scarlett 8i6 USB")]

    def test_streaming_trigger_keeps_separate_buffers_when_notes_exceed_chord_window(self) -> None:
        class FakeStreamingBatchBackend:
            def iter_messages(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                raise AssertionError("US-034 should prefer batch polling when available")

            def iter_message_batches(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                yield (
                    MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=1.0),
                    MidiMessage(message_type="note_on", note_number=64, velocity=96, channel=1, time_seconds=1.1),
                )

        class FakeAudioPlayer:
            def __init__(self):
                self.calls = []

            def play(self, buffer, device=None):
                self.calls.append((buffer.samples.shape, buffer.sample_rate, device))

        audio_player = FakeAudioPlayer()
        settings = StreamingMidiAudioTriggerSettings(
            port_name="python-d1-synth",
            max_messages=2,
            timeout_seconds=1.0,
            note_duration_seconds=0.25,
            chord_window_seconds=0.02,
        )

        result = StreamingMidiAudioTrigger(backend=FakeStreamingBatchBackend(), audio_player=audio_player).trigger(
            settings
        )

        assert result.played_event_count == 2
        assert len(audio_player.calls) == 2

    def test_streaming_trigger_groups_chord_events_even_when_batch_order_is_not_sorted(self) -> None:
        class FakeStreamingBatchBackend:
            def iter_messages(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                raise AssertionError("US-034 should prefer batch polling when available")

            def iter_message_batches(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                yield (
                    MidiMessage(message_type="note_on", note_number=67, velocity=90, channel=1, time_seconds=1.01),
                    MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=1.00),
                    MidiMessage(message_type="note_on", note_number=64, velocity=96, channel=1, time_seconds=1.005),
                )

        class FakeAudioPlayer:
            def __init__(self):
                self.calls = []

            def play(self, buffer, device=None):
                self.calls.append((buffer.samples.shape, buffer.sample_rate, device))

        audio_player = FakeAudioPlayer()
        settings = StreamingMidiAudioTriggerSettings(
            port_name="python-d1-synth",
            max_messages=3,
            timeout_seconds=1.0,
            note_duration_seconds=0.25,
            chord_window_seconds=0.02,
        )

        result = StreamingMidiAudioTrigger(backend=FakeStreamingBatchBackend(), audio_player=audio_player).trigger(
            settings
        )

        assert result.played_event_count == 3
        assert len(audio_player.calls) == 1

    def test_streaming_trigger_gated_mode_uses_note_off_duration(self) -> None:
        class FakeStreamingBackend:
            def iter_messages(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                yield MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=0.10)
                yield MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.60)
                yield MidiMessage(message_type="note_on", note_number=62, velocity=80, channel=1, time_seconds=0.80)
                yield MidiMessage(message_type="note_on", note_number=62, velocity=0, channel=1, time_seconds=1.05)

        class FakeAudioPlayer:
            def __init__(self):
                self.calls = []

            def play(self, buffer, device=None):
                self.calls.append((buffer.samples.shape, buffer.sample_rate, device))

        audio_player = FakeAudioPlayer()
        settings = StreamingMidiAudioTriggerSettings(
            port_name="python-d1-synth",
            max_messages=4,
            timeout_seconds=1.0,
            note_duration_seconds=0.25,
            voice_mode=StreamingVoiceMode.GATED,
            audio_device="Scarlett 8i6 USB",
        )

        result = StreamingMidiAudioTrigger(backend=FakeStreamingBackend(), audio_player=audio_player).trigger(settings)

        assert result.received_message_count == 4
        assert result.played_event_count == 2
        assert result.suppressed_duplicate_count == 0
        assert [f"{event.note.name}{event.note.octave}" for event in result.played_events] == ["C4", "D4"]
        assert [event.duration_seconds for event in result.played_events] == pytest.approx([0.5, 0.25])
        assert audio_player.calls == [
            ((11025, 2), 44100, "Scarlett 8i6 USB"),
            ((11025, 2), 44100, "Scarlett 8i6 USB"),
        ]

    def test_streaming_trigger_gated_mode_plays_audible_fallback_immediately_when_note_off_is_missing(self) -> None:
        class FakeStreamingBackend:
            def iter_messages(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                yield MidiMessage(message_type="note_on", note_number=64, velocity=90, channel=1, time_seconds=1.0)

        class FakeAudioPlayer:
            def __init__(self):
                self.calls = []

            def play(self, buffer, device=None):
                self.calls.append((buffer.samples.shape, buffer.sample_rate, device))

        audio_player = FakeAudioPlayer()
        settings = StreamingMidiAudioTriggerSettings(
            port_name="python-d1-synth",
            max_messages=1,
            timeout_seconds=0.1,
            note_duration_seconds=0.4,
            voice_mode=StreamingVoiceMode.GATED,
        )

        result = StreamingMidiAudioTrigger(backend=FakeStreamingBackend(), audio_player=audio_player).trigger(settings)

        assert result.played_event_count == 1
        assert result.played_events[0].note.name == "E"
        assert result.played_events[0].duration_seconds == pytest.approx(0.4)
        assert audio_player.calls == [((17640, 2), 44100, None)]

    def test_streaming_trigger_gated_mode_mixes_simultaneous_fallback_triads(self) -> None:
        class FakeStreamingBatchBackend:
            def iter_messages(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                raise AssertionError("US-034 should prefer batch polling when available")

            def iter_message_batches(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                yield (
                    MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=2.0),
                    MidiMessage(message_type="note_on", note_number=64, velocity=96, channel=1, time_seconds=2.0),
                    MidiMessage(message_type="note_on", note_number=67, velocity=90, channel=1, time_seconds=2.0),
                )
                yield (
                    MidiMessage(message_type="note_off", note_number=60, velocity=64, channel=1, time_seconds=2.5),
                    MidiMessage(message_type="note_off", note_number=64, velocity=64, channel=1, time_seconds=2.5),
                    MidiMessage(message_type="note_off", note_number=67, velocity=64, channel=1, time_seconds=2.5),
                )

        class FakeAudioPlayer:
            def __init__(self):
                self.calls = []

            def play(self, buffer, device=None):
                self.calls.append((buffer.samples.shape, buffer.sample_rate, device))

        audio_player = FakeAudioPlayer()
        settings = StreamingMidiAudioTriggerSettings(
            port_name="python-d1-synth",
            max_messages=6,
            timeout_seconds=1.0,
            note_duration_seconds=0.25,
            voice_mode=StreamingVoiceMode.GATED,
            chord_window_seconds=0.02,
        )

        result = StreamingMidiAudioTrigger(backend=FakeStreamingBatchBackend(), audio_player=audio_player).trigger(
            settings
        )

        assert result.received_message_count == 6
        assert result.played_event_count == 3
        assert [f"{event.note.name}{event.note.octave}" for event in result.played_events] == ["C4", "E4", "G4"]
        assert [event.duration_seconds for event in result.played_events] == pytest.approx([0.5, 0.5, 0.5])
        assert audio_player.calls == [((11025, 2), 44100, None)]

    def test_streaming_trigger_sustained_mode_starts_and_stops_active_voices(self) -> None:
        class FakeStreamingBatchBackend:
            def iter_messages(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                raise AssertionError("US-035 should use batch polling when available")

            def iter_message_batches(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                yield (
                    MidiMessage(message_type="note_on", note_number=60, velocity=100, channel=1, time_seconds=0.10),
                    MidiMessage(message_type="note_on", note_number=64, velocity=80, channel=1, time_seconds=0.10),
                )
                yield (
                    MidiMessage(message_type="note_off", note_number=60, velocity=64, channel=1, time_seconds=2.10),
                    MidiMessage(message_type="note_off", note_number=64, velocity=64, channel=1, time_seconds=1.10),
                )

        class FakeSustainedAudioPlayer:
            def __init__(self):
                self.calls = []

            def start(self, settings):
                self.calls.append(("start", settings.sample_rate, settings.waveform.value, settings.device))

            def note_on(self, voice_id, frequency_hz, velocity):
                self.calls.append(("note_on", voice_id, round(frequency_hz, 2), round(velocity, 3)))

            def note_off(self, voice_id):
                self.calls.append(("note_off", voice_id))

            def stop(self):
                self.calls.append(("stop",))
                return 88200

        sustained_audio_player = FakeSustainedAudioPlayer()
        settings = StreamingMidiAudioTriggerSettings(
            port_name="python-d1-synth",
            max_messages=4,
            timeout_seconds=1.0,
            note_duration_seconds=0.25,
            voice_mode=StreamingVoiceMode.SUSTAINED,
            audio_device="Scarlett 8i6 USB",
        )

        result = StreamingMidiAudioTrigger(
            backend=FakeStreamingBatchBackend(),
            sustained_audio_player=sustained_audio_player,
        ).trigger(settings)

        assert result.received_message_count == 4
        assert result.played_event_count == 2
        assert result.audio_frame_count == 88200
        assert [f"{event.note.name}{event.note.octave}" for event in result.played_events] == ["C4", "E4"]
        assert [event.duration_seconds for event in result.played_events] == pytest.approx([2.0, 1.0])
        assert sustained_audio_player.calls == [
            ("start", 44100, "sine", "Scarlett 8i6 USB"),
            ("note_on", (1, 60), 261.63, round(100 / 127, 3)),
            ("note_on", (1, 64), 329.63, round(80 / 127, 3)),
            ("note_off", (1, 60)),
            ("note_off", (1, 64)),
            ("stop",),
        ]

    def test_streaming_trigger_sustained_mode_stops_open_voices_when_note_off_is_missing(self) -> None:
        class FakeStreamingBatchBackend:
            def iter_messages(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                raise AssertionError("US-035 should use batch polling when available")

            def iter_message_batches(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                yield (MidiMessage(message_type="note_on", note_number=67, velocity=90, channel=1, time_seconds=0.50),)

        class FakeSustainedAudioPlayer:
            def __init__(self):
                self.calls = []

            def start(self, settings):
                self.calls.append(("start",))

            def note_on(self, voice_id, frequency_hz, velocity):
                self.calls.append(("note_on", voice_id))

            def note_off(self, voice_id):
                self.calls.append(("note_off", voice_id))

            def stop(self):
                self.calls.append(("stop",))
                return 11025

        sustained_audio_player = FakeSustainedAudioPlayer()

        result = StreamingMidiAudioTrigger(
            backend=FakeStreamingBatchBackend(),
            sustained_audio_player=sustained_audio_player,
        ).trigger(
            StreamingMidiAudioTriggerSettings(
                port_name="python-d1-synth",
                max_messages=1,
                timeout_seconds=0.1,
                note_duration_seconds=0.25,
                voice_mode=StreamingVoiceMode.SUSTAINED,
            )
        )

        assert result.played_event_count == 1
        assert result.played_events[0].duration_seconds == pytest.approx(0.25)
        assert sustained_audio_player.calls == [("start",), ("note_on", (1, 67)), ("note_off", (1, 67)), ("stop",)]

    def test_streaming_trigger_reports_no_audio_when_only_note_off_messages_arrive(self) -> None:
        class FakeStreamingBackend:
            def iter_messages(self, input_name, max_messages, timeout_seconds, poll_interval_seconds):
                yield MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.1)

        class FakeAudioPlayer:
            def play(self, buffer, device=None):
                raise AssertionError("note_off should not trigger audio in US-031")

        result = StreamingMidiAudioTrigger(backend=FakeStreamingBackend(), audio_player=FakeAudioPlayer()).trigger(
            StreamingMidiAudioTriggerSettings(port_name="python-d1-synth", max_messages=1, timeout_seconds=0.1)
        )

        assert result.received_message_count == 1
        assert result.played_event_count == 0
        assert result.message == (
            "Received 1 MIDI note messages from streaming virtual MIDI port python-d1-synth; no audio played."
        )

    def test_streaming_settings_require_positive_note_duration(self) -> None:
        with pytest.raises(ValueError, match="note_duration_seconds"):
            StreamingMidiAudioTriggerSettings(note_duration_seconds=0)

    def test_streaming_settings_require_positive_dedupe_window(self) -> None:
        with pytest.raises(ValueError, match="dedupe_window_seconds"):
            StreamingMidiAudioTriggerSettings(dedupe_window_seconds=0)

    def test_streaming_settings_require_positive_chord_window(self) -> None:
        with pytest.raises(ValueError, match="chord_window_seconds"):
            StreamingMidiAudioTriggerSettings(chord_window_seconds=0)

    def test_streaming_settings_require_supported_voice_mode(self) -> None:
        with pytest.raises(ValueError, match="voice_mode"):
            StreamingMidiAudioTriggerSettings(voice_mode="gated")


class TestUsbMidiHardwareInputAdapter:
    def test_any_usb_midi_input_device_can_be_selected_by_name(self) -> None:
        devices = (
            MidiDevice(identifier="input:0", name="Fishman TriplePlay", direction="input"),
            MidiDevice(identifier="input:1", name="M-Vave MIDI", direction="input"),
            MidiDevice(identifier="output:0", name="MiniFreak", direction="output"),
        )

        diagnostic = UsbMidiHardwareInputAdapter().diagnose(devices, requested_device="M-Vave")

        assert diagnostic.ready is True
        assert diagnostic.selected_device is not None
        assert diagnostic.selected_device.name == "M-Vave MIDI"
        assert "M-Vave MIDI" in diagnostic.message

    def test_output_only_devices_do_not_pass_usb_input_readiness(self) -> None:
        devices = (MidiDevice(identifier="output:0", name="Scarlett 8i6 USB", direction="output"),)

        diagnostic = UsbMidiHardwareInputAdapter().diagnose(devices)

        assert diagnostic.ready is False
        assert diagnostic.selected_device is None
        assert "No USB MIDI input devices detected" in diagnostic.message
