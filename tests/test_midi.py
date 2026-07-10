# Bestand: test_midi.py
# Versienummer: 0.1.0
# Doel: Unit tests voor MIDI discovery, selectie, virtual MIDI audio trigger en MIDI-naar-NoteEvent mapping.
# Sprint: Future MIDI/DAW
# User-Story: US-029 Logic/DAW Virtual MIDI Naar Audio Trigger
# Actie: US-029-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-029

import pytest

from synth.audio import OutputChannel
from synth.midi import (
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
    UsbMidiHardwareInputAdapter,
    VirtualMidiAudioTrigger,
    VirtualMidiAudioTriggerResult,
    VirtualMidiAudioTriggerSettings,
    VirtualMidiInputAdapter,
    VirtualMidiPortManager,
    VirtualMidiPortResult,
    VirtualMidiPortSettings,
)


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

        assert result == VirtualMidiAudioTriggerResult(
            port_name="python-d1-synth",
            received_message_count=2,
            played_event_count=1,
            audio_frame_count=4410,
            sample_rate=44100,
            message="Played 1 MIDI-triggered note events from virtual MIDI port python-d1-synth.",
        )
        assert audio_player.calls == [((4410, 2), 44100, "Scarlett 8i6 USB")]

    def test_virtual_trigger_settings_require_non_empty_port_name(self) -> None:
        with pytest.raises(ValueError, match="port_name"):
            VirtualMidiAudioTriggerSettings(port_name="")


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
