# CHATOD-20260709-D1PY-MVP-001 / US-042 MIDI Performance Patch YAML Config

- Sprintnummer: Future MIDI/DAW
- Doc versie: 0.1.0
- Status: In Review
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-042 MIDI Performance Patch YAML Config
- Actie: US-042-RED-GREEN-001

## Doel

US-042 maakt de lange `midi play-stream` performance-parameters config-file driven. De speler kan een YAML patch gebruiken voor live defaults, terwijl expliciete commandline flags blijven winnen.

## YAML Bestand

Voorbeeld:

```bash
examples/midi_performance_patch.yaml
```

De relevante sectie is:

```yaml
midi:
  performance:
    port_name: python-d1-synth
    audio_device: null
    voice_mode: sustained
    max_messages: 10000
    timeout_seconds: 600
    dedupe_window_seconds: 0.03
    chord_window_seconds: 0.08
    pitch_bend_range_semitones: 2
    pitch_bend_channel_mode: omni
    max_control_messages: 20000
    modulation_vibrato_depth_semitones: 0.25
    modulation_vibrato_rate_hz: 5
    run_until_interrupted: true
    attack_time_seconds: 0.02
    decay_time_seconds: 0.12
    sustain_level: 0.6
    release_time_seconds: 0.08
```

`audio_device` staat in het voorbeeld op `null`, zodat KodeklopperM4, MuziekM4, Spelen01 en Raspberry Pi 2 runtime devices blijven en niet als constants in de repo terechtkomen.

## Acceptatietest

Start de performance patch en kies jouw audio device expliciet op commandline:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --config examples/midi_performance_patch.yaml --audio-device "Scarlett 8i6 USB" --debuglevel verbose
```

Verwacht:

- `midi play-stream` start met `port=python-d1-synth`.
- `voice_mode=sustained` komt uit YAML.
- `pitch_bend_channel_mode=omni` komt uit YAML.
- `attack_time=0.02s`, `decay_time=0.12s`, `sustain_level=0.6` en `release_time=0.08s` komen uit YAML.
- De expliciete CLI flag `--audio-device "Scarlett 8i6 USB"` wint van YAML `audio_device: null`.
- `run_until_interrupted: true` start performance mode tot `Ctrl-C`.

## CLI Precedence

Precedence is:

1. Expliciete commandline flag.
2. `midi.performance` waarde uit YAML.
3. Bestaande veilige default.

Voorbeeld override:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --config examples/midi_performance_patch.yaml --voice-mode gated --attack-time 0.01 --audio-device "Scarlett 8i6 USB" --debuglevel verbose
```

In dat geval winnen `--voice-mode gated` en `--attack-time 0.01` van de YAML waarden.

## Scopegrenzen

- Geen GUI.
- Geen AU/VST3/plugin packaging.
- Geen nieuwe MIDI hardware constants.
- Geen hardcoded MIDI hardware device names.
- Geen automatische device selectie buiten bestaande scan/selectie routes.
- Geen wijziging aan de audio engine buiten config-defaults voor bestaande parameters.

## Traceability

- ChatID: CHATOD-20260709-D1PY-MVP-001 / US-042
- Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-042 MIDI Performance Patch YAML Config
- Version: 0.1.0
