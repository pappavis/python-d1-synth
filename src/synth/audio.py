from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np
from numpy.typing import NDArray


class OutputChannel(str, Enum):
    """Supported stereo output routing modes.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-013
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-004 Realtime CLI Playback
    - User Story: US-013 Channel Selection
    - Version: 0.1.0
    """

    STEREO = "stereo"
    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True)
class AudioBuffer:
    samples: NDArray[np.float32]
    sample_rate: int

    def duration_seconds(self) -> float:
        return float(self.samples.shape[0]) / float(self.sample_rate)


@dataclass(frozen=True)
class AudioDevice:
    identifier: str
    name: str
    host_api: str
    max_input_channels: int
    max_output_channels: int
    default_sample_rate: float

    def is_output(self) -> bool:
        return self.max_output_channels > 0


@dataclass(frozen=True)
class AudioDeviceSelection:
    sounddevice_value: int | str | None
    source: str


@dataclass(frozen=True)
class AudioDeviceScanResult:
    devices: tuple[AudioDevice, ...]
    error_message: str | None


class AudioDeviceScanner:
    def scan(self) -> AudioDeviceScanResult:
        try:
            import sounddevice
        except ImportError:
            return AudioDeviceScanResult(
                devices=tuple(),
                error_message="sounddevice is not installed. Install project dependencies before scanning audio devices.",
            )

        try:
            raw_devices = sounddevice.query_devices()
            host_apis = sounddevice.query_hostapis()
        except Exception as exc:
            return AudioDeviceScanResult(devices=tuple(), error_message=f"sounddevice query failed: {exc}")

        devices: list[AudioDevice] = []
        for index, raw in enumerate(raw_devices):
            raw_mapping = dict(raw)
            host_api_index = int(raw_mapping.get("hostapi", -1))
            host_api_name = self._host_api_name(host_apis, host_api_index)
            devices.append(
                AudioDevice(
                    identifier=str(index),
                    name=str(raw_mapping.get("name", "")),
                    host_api=host_api_name,
                    max_input_channels=int(raw_mapping.get("max_input_channels", 0)),
                    max_output_channels=int(raw_mapping.get("max_output_channels", 0)),
                    default_sample_rate=float(raw_mapping.get("default_samplerate", 0.0)),
                )
            )
        return AudioDeviceScanResult(devices=tuple(devices), error_message=None)

    def list_devices(self) -> tuple[AudioDevice, ...]:
        return self.scan().devices

    def _host_api_name(self, host_apis: Any, index: int) -> str:
        try:
            host_api = host_apis[index]
            return str(dict(host_api).get("name", "unknown"))
        except (IndexError, TypeError, ValueError):
            return "unknown"


class AudioDeviceSelector:
    def select(self, cli_device: str | None) -> AudioDeviceSelection:
        if cli_device is None or cli_device == "":
            return AudioDeviceSelection(sounddevice_value=None, source="default")
        if cli_device.isdigit():
            return AudioDeviceSelection(sounddevice_value=int(cli_device), source="cli")
        return AudioDeviceSelection(sounddevice_value=cli_device, source="cli")


class ChannelRouter:
    """Route mono synth samples to stereo, left-only, or right-only output.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-013
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-004 Realtime CLI Playback
    - User Story: US-013 Channel Selection
    - Version: 0.1.0
    """

    def route(self, mono_samples: NDArray[np.float32], channel: OutputChannel) -> NDArray[np.float32]:
        silent = np.zeros_like(mono_samples)
        if channel is OutputChannel.STEREO:
            return np.column_stack((mono_samples, mono_samples)).astype(np.float32)
        if channel is OutputChannel.LEFT:
            return np.column_stack((mono_samples, silent)).astype(np.float32)
        if channel is OutputChannel.RIGHT:
            return np.column_stack((silent, mono_samples)).astype(np.float32)
        raise ValueError(f"Unsupported output channel '{channel}'")


class SoundDeviceAudioPlayer:
    def play(self, buffer: AudioBuffer, device: int | str | None = None) -> None:
        try:
            import sounddevice
        except ImportError as exc:
            raise RuntimeError("sounddevice is not installed. Install project dependencies before realtime playback.") from exc

        try:
            sounddevice.play(buffer.samples, samplerate=buffer.sample_rate, device=device)
            sounddevice.wait()
        except Exception as exc:
            raise RuntimeError(
                "Audio playback failed. Run 'python -m synth audio list-devices' and retry with --audio-device."
            ) from exc
