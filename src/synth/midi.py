from dataclasses import dataclass
import json
import platform
import subprocess
import sys

from synth.notes import NoteEvent, NoteParser, NoteSequence


@dataclass(frozen=True)
class MidiDevice:
    identifier: str
    name: str
    direction: str


@dataclass(frozen=True)
class MidiDeviceSelection:
    selected_device: str | None
    source: str


@dataclass(frozen=True)
class MidiDeviceScanResult:
    """Result for safe MIDI device discovery diagnostics.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-022-BLOCKER
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-022 USB MIDI Hardware Input
    - Version: 0.1.0
    """

    devices: tuple[MidiDevice, ...]
    error_message: str | None
    backend_name: str = "mido/python-rtmidi"
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class MidiMessage:
    """Protocol-level MIDI message normalized for virtual input tests.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-020
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-020 Virtual MIDI Input Voor DAW
    - Version: 0.1.0
    """

    message_type: str
    note_number: int
    velocity: int
    channel: int
    time_seconds: float = 0.0

    def __post_init__(self) -> None:
        if self.message_type not in {"note_on", "note_off"}:
            raise ValueError("message_type must be note_on or note_off")
        if not 0 <= self.note_number <= 127:
            raise ValueError("note_number must be between 0 and 127")
        if not 0 <= self.velocity <= 127:
            raise ValueError("velocity must be between 0 and 127")
        if not 1 <= self.channel <= 16:
            raise ValueError("channel must be between 1 and 16")
        if self.time_seconds < 0:
            raise ValueError("time_seconds must not be negative")


@dataclass(frozen=True)
class VirtualMidiInputSettings:
    """Settings for future virtual MIDI input routes from a DAW.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-020
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-020 Virtual MIDI Input Voor DAW
    - Version: 0.1.0
    """

    input_name: str = "python-d1-synth"
    default_note_duration_seconds: float = 1.0

    def __post_init__(self) -> None:
        if not self.input_name.strip():
            raise ValueError("input_name must not be empty")
        if self.default_note_duration_seconds <= 0:
            raise ValueError("default_note_duration_seconds must be positive")


@dataclass(frozen=True)
class VirtualMidiInputDiagnostic:
    """Diagnostic result for a virtual MIDI input route.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-020
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-020 Virtual MIDI Input Voor DAW
    - Version: 0.1.0
    """

    available: bool
    message: str


@dataclass(frozen=True)
class UsbMidiInputDiagnostic:
    """Readiness result for generic USB MIDI input hardware.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-022
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-022 USB MIDI Hardware Input
    - Version: 0.1.0
    """

    ready: bool
    message: str
    selected_device: MidiDevice | None
    compatible_devices: tuple[MidiDevice, ...]


class UsbMidiHardwareInputAdapter:
    """Diagnose generic USB MIDI input devices before live receive is enabled.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-022
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-022 USB MIDI Hardware Input
    - Version: 0.1.0
    """

    def diagnose(self, devices: tuple[MidiDevice, ...], requested_device: str | None = None) -> UsbMidiInputDiagnostic:
        input_devices = tuple(device for device in devices if device.direction == "input")
        if not input_devices:
            return UsbMidiInputDiagnostic(
                ready=False,
                message=(
                    "No USB MIDI input devices detected. Connect any class-compliant USB MIDI interface and run "
                    "the diagnostic again."
                ),
                selected_device=None,
                compatible_devices=tuple(),
            )

        selected = self._select_device(input_devices, requested_device)
        if selected is None:
            names = ", ".join(device.name for device in input_devices)
            return UsbMidiInputDiagnostic(
                ready=False,
                message=f"Requested USB MIDI input device not found. Available input devices: {names}.",
                selected_device=None,
                compatible_devices=input_devices,
            )

        return UsbMidiInputDiagnostic(
            ready=True,
            message=f"USB MIDI input ready: {selected.name} ({selected.identifier}).",
            selected_device=selected,
            compatible_devices=input_devices,
        )

    def _select_device(self, devices: tuple[MidiDevice, ...], requested_device: str | None) -> MidiDevice | None:
        if requested_device is None:
            return devices[0]
        normalized = requested_device.casefold()
        for device in devices:
            if normalized in device.name.casefold() or normalized == device.identifier.casefold():
                return device
        return None


class VirtualMidiInputAdapter:
    """Map virtual MIDI note messages to the internal note sequence model.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-020
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-020 Virtual MIDI Input Voor DAW
    - Version: 0.1.0
    """

    def __init__(self, settings: VirtualMidiInputSettings | None = None) -> None:
        self._settings = settings if settings is not None else VirtualMidiInputSettings()
        self._parser = NoteParser()

    def diagnose(self, backend_available: bool) -> VirtualMidiInputDiagnostic:
        if backend_available:
            return VirtualMidiInputDiagnostic(
                available=True,
                message=(
                    f"Virtual MIDI input backend is installed. Route a DAW track to '{self._settings.input_name}' "
                    "when the live input story opens the port."
                ),
            )
        return VirtualMidiInputDiagnostic(
            available=False,
            message=(
                "Virtual MIDI input backend is not available. Install the MIDI extras and verify a virtual MIDI "
                "route before DAW input."
            ),
        )

    def messages_to_note_sequence(self, messages: tuple[MidiMessage, ...]) -> NoteSequence:
        active_notes: dict[tuple[int, int], MidiMessage] = {}
        events: list[NoteEvent] = []

        for message in messages:
            key = (message.channel, message.note_number)
            if message.message_type == "note_on" and message.velocity > 0:
                active_notes[key] = message
                continue

            started = active_notes.pop(key, None)
            if started is not None:
                events.append(self._event_from_pair(started, message))

        for started in active_notes.values():
            events.append(self._event_from_open_note(started))

        return NoteSequence(events=tuple(sorted(events, key=lambda event: event.start_seconds)))

    def _event_from_pair(self, started: MidiMessage, stopped: MidiMessage) -> NoteEvent:
        duration = stopped.time_seconds - started.time_seconds
        if duration <= 0:
            duration = self._settings.default_note_duration_seconds
        return NoteEvent(
            note=self._note_from_midi_number(started.note_number),
            duration_seconds=duration,
            velocity=started.velocity / 127,
            start_seconds=started.time_seconds,
        )

    def _event_from_open_note(self, started: MidiMessage) -> NoteEvent:
        return NoteEvent(
            note=self._note_from_midi_number(started.note_number),
            duration_seconds=self._settings.default_note_duration_seconds,
            velocity=started.velocity / 127,
            start_seconds=started.time_seconds,
        )

    def _note_from_midi_number(self, note_number: int):
        note_names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
        octave = (note_number // 12) - 1
        name = note_names[note_number % 12]
        return self._parser.parse(f"{name}{octave}")


class MidiDeviceScanner:
    """Safe MIDI device scanner with macOS CoreMIDI crash isolation.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-022-BLOCKER
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-022 USB MIDI Hardware Input
    - Version: 0.1.0
    """

    _BACKEND_NAME = "mido/python-rtmidi"

    def __init__(self, allow_unsafe_native_scan: bool = False) -> None:
        self._allow_unsafe_native_scan = allow_unsafe_native_scan

    def scan(self) -> MidiDeviceScanResult:
        if platform.system() == "Darwin" and not self._allow_unsafe_native_scan:
            return MidiDeviceScanResult(
                devices=tuple(),
                error_message=(
                    "Native RtMidi/CoreMIDI scanning is disabled by default on macOS because it can abort the "
                    "Python process. Use --unsafe-rtmidi-scan only when you intentionally want to test it."
                ),
                backend_name=self._BACKEND_NAME,
            )
        return self._scan_with_mido_subprocess()

    def list_devices(self) -> tuple[MidiDevice, ...]:
        return self.scan().devices

    def _scan_with_mido_subprocess(self) -> MidiDeviceScanResult:
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
            return MidiDeviceScanResult(
                devices=tuple(),
                error_message="MIDI device scan subprocess failed.",
                backend_name=self._BACKEND_NAME,
            )
        if completed.returncode != 0:
            return MidiDeviceScanResult(
                devices=tuple(),
                error_message="MIDI backend failed while scanning devices.",
                backend_name=self._BACKEND_NAME,
                returncode=completed.returncode,
                stdout=completed.stdout.strip(),
                stderr=completed.stderr.strip(),
            )

        try:
            raw_devices = json.loads(completed.stdout)
        except json.JSONDecodeError:
            return MidiDeviceScanResult(
                devices=tuple(),
                error_message="MIDI backend returned invalid scan data.",
                backend_name=self._BACKEND_NAME,
                returncode=completed.returncode,
                stdout=completed.stdout.strip(),
                stderr=completed.stderr.strip(),
            )

        devices = tuple(
            MidiDevice(
                identifier=str(raw["identifier"]),
                name=str(raw["name"]),
                direction=str(raw["direction"]),
            )
            for raw in raw_devices
            if isinstance(raw, dict)
        )
        return MidiDeviceScanResult(
            devices=devices,
            error_message=None,
            backend_name=self._BACKEND_NAME,
            returncode=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
        )


class MidiDeviceSelector:
    def select(self, cli_device: str | None, config_device: str | None) -> MidiDeviceSelection:
        if cli_device:
            return MidiDeviceSelection(selected_device=cli_device, source="cli")
        if config_device:
            return MidiDeviceSelection(selected_device=config_device, source="config")
        return MidiDeviceSelection(selected_device=None, source="none")
