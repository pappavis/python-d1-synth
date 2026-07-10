import os

import pytest

from synth.midi import MidiDeviceScanner


@pytest.mark.hardware_midi
class TestHardwareMidiDeviceScan:
    """Manual US-022 hardware scanner test.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-022-BLOCKER
    - Backlog: Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-022 USB MIDI Hardware Input
    - Version: 0.1.0
    """

    def test_scans_and_lists_connected_midi_devices(self, capsys) -> None:
        if os.environ.get("PYTHON_D1_RUN_HARDWARE_MIDI") != "1":
            pytest.skip("Set PYTHON_D1_RUN_HARDWARE_MIDI=1 to run the real US-022 MIDI hardware scan.")

        result = MidiDeviceScanner(allow_unsafe_native_scan=True).scan()

        print(f"MIDI backend: {result.backend_name}")
        if result.returncode is not None:
            print(f"MIDI backend return code: {result.returncode}")
        if result.stderr:
            print(f"MIDI backend stderr: {result.stderr.splitlines()[-1]}")
        if result.stdout:
            print(f"MIDI backend stdout: {result.stdout.splitlines()[-1]}")
        if result.error_message is not None:
            print(result.error_message)
        for device in result.devices:
            print(f"{device.identifier}\t{device.direction}\t{device.name}")

        captured = capsys.readouterr()
        if not result.devices:
            pytest.fail(
                "BLOCKER: No MIDI devices found by Python. Logic/Audio MIDI Setup is expected to show connected "
                f"devices. Scanner output:\n{captured.out}"
            )
