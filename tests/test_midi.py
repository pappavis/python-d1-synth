from synth.midi import (
    MidiDevice,
    MidiDeviceScanner,
    MidiDeviceSelector,
    MidiMessage,
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
