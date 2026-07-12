# Bestand: audio.py
# Versienummer: 0.1.0
# Doel: Audio buffers, device selectie, routing en sustained streaming output.
# Sprint: Future MIDI/DAW
# User-Story: US-041 Amp Envelope ADSR Parameters
# Actie: US-041-RED-GREEN-001
# ChatID: CHATOD-20260709-D1PY-MVP-001 / US-041

from dataclasses import dataclass
from enum import Enum
import math
import threading
from typing import Any

import numpy as np
from numpy.typing import NDArray

from synth.oscillators import Waveform


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


@dataclass(frozen=True)
class SustainedAudioPlayerSettings:
    """Settings for sustained streaming audio output.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-035
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-035 Sustained Note Audio Engine
    - User Story: US-040 Envelope Release / Soft Note-Off
    - User Story: US-041 Amp Envelope ADSR Parameters
    - Version: 0.1.0
    """

    sample_rate: int
    waveform: Waveform
    amplitude: float
    channel: OutputChannel
    device: int | str | None = None
    attack_seconds: float = 0.0
    decay_seconds: float = 0.0
    sustain_level: float = 1.0
    release_seconds: float = 0.03

    def __post_init__(self) -> None:
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if not 0 < self.amplitude <= 1.0:
            raise ValueError("amplitude must be between 0 and 1")
        if self.attack_seconds < 0:
            raise ValueError("attack_seconds must not be negative")
        if self.decay_seconds < 0:
            raise ValueError("decay_seconds must not be negative")
        if not 0 <= self.sustain_level <= 1.0:
            raise ValueError("sustain_level must be between 0 and 1")
        if self.release_seconds < 0:
            raise ValueError("release_seconds must not be negative")


@dataclass
class SustainedVoiceState:
    """Mutable oscillator state for one active sustained MIDI voice.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-035
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-035 Sustained Note Audio Engine
    - User Story: US-036 MIDI Pitch Bend Mapping En DSP
    - User Story: US-037 MIDI Modulation CC1 Mapping En DSP
    - User Story: US-040 Envelope Release / Soft Note-Off
    - User Story: US-041 Amp Envelope ADSR Parameters
    - Version: 0.1.0
    """

    base_frequency_hz: float
    frequency_hz: float
    velocity: float
    phase_cycles: float = 0.0
    modulation_depth_semitones: float = 0.0
    modulation_rate_hz: float = 5.0
    lfo_phase_cycles: float = 0.0
    age_frames: int = 0
    release_remaining_frames: int = 0
    release_total_frames: int = 0
    release_start_level: float = 1.0


class SoundDeviceSustainedAudioPlayer:
    """Stream active sustained voices until their note-off messages arrive.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-035
    - Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
    - Epic: EPIC-007 Future MIDI En DAW Integratie
    - User Story: US-035 Sustained Note Audio Engine
    - User Story: US-036 MIDI Pitch Bend Mapping En DSP
    - User Story: US-037 MIDI Modulation CC1 Mapping En DSP
    - User Story: US-040 Envelope Release / Soft Note-Off
    - User Story: US-041 Amp Envelope ADSR Parameters
    - Version: 0.1.0
    """

    def __init__(self, channel_router: ChannelRouter | None = None) -> None:
        self._channel_router = channel_router if channel_router is not None else ChannelRouter()
        self._lock = threading.RLock()
        self._voice_by_id: dict[tuple[int, int], SustainedVoiceState] = {}
        self._settings: SustainedAudioPlayerSettings | None = None
        self._stream = None
        self._rendered_frame_count = 0

    def start(self, settings: SustainedAudioPlayerSettings) -> None:
        try:
            import sounddevice
        except ImportError as exc:
            raise RuntimeError(
                "sounddevice is not installed. Install project dependencies before sustained playback."
            ) from exc

        stream = sounddevice.OutputStream(
            samplerate=settings.sample_rate,
            channels=2,
            dtype="float32",
            device=settings.device,
            callback=self._callback,
        )
        with self._lock:
            self._settings = settings
            self._rendered_frame_count = 0
            self._voice_by_id.clear()
            self._stream = stream
        stream.start()

    def note_on(self, voice_id: tuple[int, int], frequency_hz: float, velocity: float) -> None:
        with self._lock:
            self._voice_by_id[voice_id] = SustainedVoiceState(
                base_frequency_hz=frequency_hz,
                frequency_hz=frequency_hz,
                velocity=velocity,
            )

    def note_off(self, voice_id: tuple[int, int]) -> None:
        with self._lock:
            voice = self._voice_by_id.get(voice_id)
            settings = self._settings
            if voice is None:
                return
            if settings is None or settings.release_seconds == 0:
                self._voice_by_id.pop(voice_id, None)
                return
            release_frames = max(1, int(round(settings.release_seconds * settings.sample_rate)))
            release_start_level = self._active_envelope_level(settings, voice.age_frames)
            self._voice_by_id[voice_id] = SustainedVoiceState(
                base_frequency_hz=voice.base_frequency_hz,
                frequency_hz=voice.frequency_hz,
                velocity=voice.velocity,
                phase_cycles=voice.phase_cycles,
                modulation_depth_semitones=voice.modulation_depth_semitones,
                modulation_rate_hz=voice.modulation_rate_hz,
                lfo_phase_cycles=voice.lfo_phase_cycles,
                age_frames=voice.age_frames,
                release_remaining_frames=release_frames,
                release_total_frames=release_frames,
                release_start_level=release_start_level,
            )

    def pitch_bend(self, channel: int, semitones: float) -> None:
        bend_ratio = math.pow(2.0, semitones / 12.0)
        with self._lock:
            for voice_id, voice in tuple(self._voice_by_id.items()):
                voice_channel, _note_number = voice_id
                if voice_channel != channel:
                    continue
                self._voice_by_id[voice_id] = SustainedVoiceState(
                    base_frequency_hz=voice.base_frequency_hz,
                    frequency_hz=voice.base_frequency_hz * bend_ratio,
                    velocity=voice.velocity,
                    phase_cycles=voice.phase_cycles,
                    modulation_depth_semitones=voice.modulation_depth_semitones,
                    modulation_rate_hz=voice.modulation_rate_hz,
                    lfo_phase_cycles=voice.lfo_phase_cycles,
                    age_frames=voice.age_frames,
                    release_remaining_frames=voice.release_remaining_frames,
                    release_total_frames=voice.release_total_frames,
                    release_start_level=voice.release_start_level,
                )

    def modulation(self, channel: int, depth_semitones: float, rate_hz: float) -> None:
        with self._lock:
            for voice_id, voice in tuple(self._voice_by_id.items()):
                voice_channel, _note_number = voice_id
                if voice_channel != channel:
                    continue
                self._voice_by_id[voice_id] = SustainedVoiceState(
                    base_frequency_hz=voice.base_frequency_hz,
                    frequency_hz=voice.frequency_hz,
                    velocity=voice.velocity,
                    phase_cycles=voice.phase_cycles,
                    modulation_depth_semitones=depth_semitones,
                    modulation_rate_hz=rate_hz,
                    lfo_phase_cycles=voice.lfo_phase_cycles,
                    age_frames=voice.age_frames,
                    release_remaining_frames=voice.release_remaining_frames,
                    release_total_frames=voice.release_total_frames,
                    release_start_level=voice.release_start_level,
                )

    def stop(self) -> int:
        with self._lock:
            stream = self._stream
            self._stream = None
            self._voice_by_id.clear()
            rendered_frame_count = self._rendered_frame_count
        if stream is not None:
            stream.stop()
            stream.close()
        return rendered_frame_count

    def abort(self) -> int:
        with self._lock:
            stream = self._stream
            self._stream = None
            self._voice_by_id.clear()
            rendered_frame_count = self._rendered_frame_count
        if stream is not None:
            abort = getattr(stream, "abort", None)
            if callable(abort):
                abort()
            else:
                stream.stop()
            stream.close()
        return rendered_frame_count

    def active_voice_count(self) -> int:
        with self._lock:
            return len(self._voice_by_id)

    def _callback(self, outdata, frames, time_info, status) -> None:
        del time_info, status
        with self._lock:
            settings = self._settings
            voice_items = tuple(self._voice_by_id.items())
        if settings is None:
            outdata[:] = np.zeros((frames, 2), dtype=np.float32)
            return

        mono = np.zeros(frames, dtype=np.float32)
        updated_voices: dict[tuple[int, int], SustainedVoiceState] = {}
        completed_voice_ids: list[tuple[int, int]] = []
        timeline = np.arange(frames, dtype=np.float64) / settings.sample_rate
        for voice_id, voice in voice_items:
            instantaneous_frequency = self._modulated_frequency(voice, timeline)
            increments = instantaneous_frequency / settings.sample_rate
            phase = voice.phase_cycles + np.cumsum(increments) - increments[0]
            envelope = self._amplitude_envelope(settings, voice, frames)
            mono += self._waveform_samples(settings.waveform, phase) * settings.amplitude * voice.velocity * envelope
            updated_phase = float((voice.phase_cycles + float(np.sum(increments))) % 1.0)
            updated_lfo_phase = float((voice.lfo_phase_cycles + frames * voice.modulation_rate_hz / settings.sample_rate) % 1.0)
            updated_age_frames = voice.age_frames + frames
            release_remaining_frames = max(0, voice.release_remaining_frames - frames)
            if voice.release_total_frames > 0 and release_remaining_frames == 0:
                completed_voice_ids.append(voice_id)
                continue
            updated_voices[voice_id] = SustainedVoiceState(
                base_frequency_hz=voice.base_frequency_hz,
                frequency_hz=voice.frequency_hz,
                velocity=voice.velocity,
                phase_cycles=updated_phase,
                modulation_depth_semitones=voice.modulation_depth_semitones,
                modulation_rate_hz=voice.modulation_rate_hz,
                lfo_phase_cycles=updated_lfo_phase,
                age_frames=updated_age_frames,
                release_remaining_frames=release_remaining_frames,
                release_total_frames=voice.release_total_frames,
                release_start_level=voice.release_start_level,
            )

        mono = np.clip(mono, -1.0, 1.0).astype(np.float32)
        outdata[:] = self._channel_router.route(mono, settings.channel)
        with self._lock:
            for voice_id in completed_voice_ids:
                self._voice_by_id.pop(voice_id, None)
            for voice_id, voice in updated_voices.items():
                if voice_id in self._voice_by_id:
                    self._voice_by_id[voice_id] = voice
            self._rendered_frame_count += frames

    def _modulated_frequency(self, voice: SustainedVoiceState, timeline: NDArray[np.float64]) -> NDArray[np.float64]:
        if voice.modulation_depth_semitones == 0.0:
            return np.full(timeline.shape, voice.frequency_hz, dtype=np.float64)
        lfo_phase = voice.lfo_phase_cycles + voice.modulation_rate_hz * timeline
        semitone_offset = voice.modulation_depth_semitones * np.sin(2.0 * np.pi * lfo_phase)
        return voice.frequency_hz * np.power(2.0, semitone_offset / 12.0)

    def _amplitude_envelope(
        self,
        settings: SustainedAudioPlayerSettings,
        voice: SustainedVoiceState,
        frames: int,
    ) -> NDArray[np.float32]:
        if voice.release_total_frames == 0:
            frame_positions = voice.age_frames + np.arange(frames, dtype=np.float64)
            return self._active_envelope(settings, frame_positions).astype(np.float32)
        remaining = voice.release_remaining_frames - np.arange(frames, dtype=np.float64)
        envelope = np.clip(remaining / voice.release_total_frames, 0.0, 1.0) * voice.release_start_level
        return envelope.astype(np.float32)

    def _active_envelope(self, settings: SustainedAudioPlayerSettings, frame_positions: NDArray[np.float64]) -> NDArray[np.float64]:
        attack_frames = int(round(settings.attack_seconds * settings.sample_rate))
        decay_frames = int(round(settings.decay_seconds * settings.sample_rate))
        levels = np.full(frame_positions.shape, settings.sustain_level, dtype=np.float64)
        if attack_frames > 0:
            attack_mask = frame_positions < attack_frames
            levels[attack_mask] = (frame_positions[attack_mask] + 1.0) / attack_frames
        else:
            attack_mask = np.zeros(frame_positions.shape, dtype=bool)
        if decay_frames > 0:
            decay_start = attack_frames
            decay_end = decay_start + decay_frames
            decay_mask = (frame_positions >= decay_start) & (frame_positions < decay_end)
            decay_progress = (frame_positions[decay_mask] - decay_start + 1.0) / decay_frames
            levels[decay_mask] = 1.0 + (settings.sustain_level - 1.0) * decay_progress
        elif attack_frames == 0:
            levels[~attack_mask] = settings.sustain_level
        return np.clip(levels, 0.0, 1.0)

    def _active_envelope_level(self, settings: SustainedAudioPlayerSettings, age_frames: int) -> float:
        return float(self._active_envelope(settings, np.array([age_frames], dtype=np.float64))[0])

    def _waveform_samples(self, waveform: Waveform, phase: NDArray[np.float64]) -> NDArray[np.float32]:
        if waveform is Waveform.SINE:
            return np.sin(2.0 * np.pi * phase).astype(np.float32)
        if waveform is Waveform.SAW:
            return (2.0 * (phase - np.floor(phase + 0.5))).astype(np.float32)
        if waveform is Waveform.SQUARE:
            return np.where(np.sin(2.0 * np.pi * phase) >= 0.0, 1.0, -1.0).astype(np.float32)
        raise ValueError(f"Unsupported waveform '{waveform}'")


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
