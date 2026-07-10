# Bestand: test_midi.py
# Versienummer: 0.1.0
# Doel: Unit tests voor MIDI discovery, selectie en MIDI-naar-NoteEvent mapping.
# Sprint: Future MIDI/DAW
# User-Story: US-024 MIDI Naar NoteEvent Mapping
# Actie: US-024-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-024

import pytest

from synth.midi import (
    MidiDevice,
    MidiDeviceScanner,
    MidiDeviceSelector,
    MidiMessage,
    MidiToNoteEventMapper,
    UsbMidiHardwareInputAdapter,
    VirtualMidiInputAdapter,
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
