from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import NDArray


class Waveform(str, Enum):
    SINE = "sine"
    SAW = "saw"
    SQUARE = "square"


@dataclass(frozen=True)
class OscillatorSettings:
    waveform: Waveform
    sample_rate: int
    amplitude: float

    def __post_init__(self) -> None:
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if not 0.0 <= self.amplitude <= 1.0:
            raise ValueError("amplitude must be between 0.0 and 1.0")


class Oscillator:
    def __init__(self, settings: OscillatorSettings) -> None:
        self._settings = settings

    def generate(self, frequency_hz: float, duration_seconds: float) -> NDArray[np.float32]:
        if frequency_hz <= 0:
            raise ValueError("frequency_hz must be positive")
        if duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")

        sample_count = int(round(self._settings.sample_rate * duration_seconds))
        timeline = np.arange(sample_count, dtype=np.float64) / self._settings.sample_rate
        phase = frequency_hz * timeline

        if self._settings.waveform is Waveform.SINE:
            samples = np.sin(2.0 * np.pi * phase)
        elif self._settings.waveform is Waveform.SAW:
            samples = 2.0 * (phase - np.floor(phase + 0.5))
        elif self._settings.waveform is Waveform.SQUARE:
            samples = np.where(np.sin(2.0 * np.pi * phase) >= 0.0, 1.0, -1.0)
        else:
            raise ValueError(f"Unsupported waveform '{self._settings.waveform}'")

        return (samples * self._settings.amplitude).astype(np.float32)

