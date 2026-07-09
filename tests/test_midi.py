from synth.midi import MidiDeviceScanner, MidiDeviceSelector


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
    def test_scanner_returns_tuple_when_backend_unavailable_or_blocked(self) -> None:
        devices = MidiDeviceScanner().list_devices()

        assert isinstance(devices, tuple)
