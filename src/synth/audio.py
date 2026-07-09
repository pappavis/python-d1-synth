from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import NDArray


class OutputChannel(str, Enum):
    STEREO = "stereo"
    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True)
class AudioBuffer:
    samples: NDArray[np.float32]
    sample_rate: int

    def duration_seconds(self) -> float:
        return float(self.samples.shape[0]) / float(self.sample_rate)


class ChannelRouter:
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
    def play(self, buffer: AudioBuffer) -> None:
        try:
            import sounddevice
        except ImportError as exc:
            raise RuntimeError("sounddevice is not installed. Install project dependencies before realtime playback.") from exc

        sounddevice.play(buffer.samples, samplerate=buffer.sample_rate)
        sounddevice.wait()

