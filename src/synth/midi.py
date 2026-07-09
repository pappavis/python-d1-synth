from dataclasses import dataclass
import json
import subprocess
import sys


@dataclass(frozen=True)
class MidiDevice:
    identifier: str
    name: str
    direction: str


@dataclass(frozen=True)
class MidiDeviceSelection:
    selected_device: str | None
    source: str


class MidiDeviceScanner:
    def list_devices(self) -> tuple[MidiDevice, ...]:
        scan_code = """
import json
try:
    import mido
except ImportError:
    print(json.dumps([]))
    raise SystemExit(0)

devices = []
for index, name in enumerate(mido.get_input_names()):
    devices.append({"identifier": f"input:{index}", "name": name, "direction": "input"})
for index, name in enumerate(mido.get_output_names()):
    devices.append({"identifier": f"output:{index}", "name": name, "direction": "output"})
print(json.dumps(devices))
"""
        try:
            completed = subprocess.run(
                [sys.executable, "-c", scan_code],
                capture_output=True,
                check=False,
                text=True,
                timeout=5.0,
            )
        except (OSError, subprocess.SubprocessError):
            return tuple()
        if completed.returncode != 0:
            return tuple()

        try:
            raw_devices = json.loads(completed.stdout)
        except json.JSONDecodeError:
            return tuple()

        return tuple(
            MidiDevice(
                identifier=str(raw["identifier"]),
                name=str(raw["name"]),
                direction=str(raw["direction"]),
            )
            for raw in raw_devices
            if isinstance(raw, dict)
        )


class MidiDeviceSelector:
    def select(self, cli_device: str | None, config_device: str | None) -> MidiDeviceSelection:
        if cli_device:
            return MidiDeviceSelection(selected_device=cli_device, source="cli")
        if config_device:
            return MidiDeviceSelection(selected_device=config_device, source="config")
        return MidiDeviceSelection(selected_device=None, source="none")
