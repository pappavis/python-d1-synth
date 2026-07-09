# python-d1-synth

ChatOD: CHATOD-20260709-D1PY-MVP-001 / SKELETON-001

`python-d1-synth` is een commandline-first Python monosynth MVP, geinspireerd door klassieke subtractive monosynth workflows. Sprint 1 richt zich op hoorbare audio, WAV-rendering, note parsing, testbare architectuur en later uitbreidbare MIDI/DAW-integratie.

## Development Environment

Target:

- macOS op Mac Mini M4.
- Python 3.11.
- VS Code.
- Virtual environment opgegeven door klant: `/Users/michiele/venv`.
- Gedetecteerde uitvoerbare interpreter uit je `.zshrc`: `/Volumes/data1/michiele/venv/venv3.12/bin/python`.

Let op: in je `.zshrc` activeer je `/Volumes/data1/michiele/venv/venv3.12/bin/activate`. De werkende Python interpreter staat daardoor op `/Volumes/data1/michiele/venv/venv3.12/bin/python`.

## Install

```bash
cd /Volumes/data1/Yandex.Disk.localized/michiele/Programmering/Python/python_normaal/github_python_normaal/desktop_synth
/Volumes/data1/michiele/venv/venv3.12/bin/python -m pip install -e ".[dev,midi]"
```

Wanneer jouw lokale Python 3.11 venv op een ander subpad staat, vervang dan `/Volumes/data1/michiele/venv/venv3.12/bin/python` door het juiste pad.

## Run CLI

Render een WAV-bestand:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth render examples/patch.yaml --output outputs/demo.wav --debuglevel light
```

Speel een noot:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --note C3 --duration 1.0 --channel stereo --debuglevel light
```

Speel een noot via je Scarlett 8i6 USB:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --note C3 --duration 1.0 --channel stereo --audio-device "Scarlett 8i6 USB" --debuglevel verbose
```

Speel een testsequence:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --testsequence "ACGD" --duration 0.25 --debuglevel light
```

Scan audio devices:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth audio list-devices --debuglevel light
```

Scan MIDI devices:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi list-devices --debuglevel light
```

Selecteer later een MIDI device:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --midi-device "Arturia KeyLab Mk3" --debuglevel light
```

## Tests

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m pytest
```

De testcode gebruikt `pytest` en volgt de afgesproken red/green werkwijze per user story.

## VS Code

Open deze map als workspace:

```bash
code /Volumes/data1/Yandex.Disk.localized/michiele/Programmering/Python/python_normaal/github_python_normaal/desktop_synth
```

De launch-config bevat:

- `python-d1-synth: play C3`
- `python-d1-synth: play C3 Scarlett`
- `python-d1-synth: render patch`
- `python-d1-synth: list audio devices`
- `python-d1-synth: list MIDI devices`

Als VS Code jouw venv niet automatisch kiest, zet de interpreter handmatig naar jouw daadwerkelijke venv-python.

## MIDI Troubleshooting

Op macOS kan `python-rtmidi`/CoreMIDI hard aborten bij device discovery, bijvoorbeeld met `MidiInCore::initialize: error creating OS-X MIDI client object (-10833)`. De crashrapporten die tijdens US-011 zijn bekeken wijzen naar `_rtmidi` en CoreMIDI. Dat is de MIDI-scanroute, niet de audio-outputroute naar bijvoorbeeld `Scarlett 8i6 USB`.

De skeleton voert MIDI device scanning daarom in een apart subprocess uit. Als RtMidi crasht, blijft de hoofd-CLI overeind en meldt `midi list-devices` dat er geen devices gevonden zijn of dat de backend niet bruikbaar is.

Vanaf US-011 is native RtMidi/CoreMIDI scanning op macOS standaard uitgeschakeld, omdat macOS alsnog crashrapporten toont wanneer alleen het scan-subprocess abort. De veilige default is:

```bash
PYTHONPATH=src python -m synth midi list-devices --debuglevel light
```

Alleen voor bewuste backenddiagnose:

```bash
PYTHONPATH=src python -m synth midi list-devices --unsafe-rtmidi-scan --debuglevel verbose
```

## Audio Troubleshooting

Je macOS audio-instellingen tonen `Scarlett 8i6 USB` als outputdevice/default. Test eerst vanuit je gewone Terminal, niet vanuit een gesandboxte Codex-run:

```bash
cd /Volumes/data1/Yandex.Disk.localized/michiele/Programmering/Python/python_normaal/github_python_normaal/desktop_synth
source /Volumes/data1/michiele/venv/venv3.12/bin/activate
PYTHONPATH=src python -m synth audio list-devices --debuglevel verbose
PYTHONPATH=src python -m synth play --note C3 --duration 1.0 --channel stereo --audio-device "Scarlett 8i6 USB" --debuglevel verbose
```

Als `audio list-devices` geen devices toont in Codex maar macOS ze wel toont, is dat waarschijnlijk sessie-/permissioncontext. Voer de test dan direct in je eigen Terminal of VS Code terminal uit.

## Sprint 1 Scope

In scope:

- CLI skeleton.
- Note parsing.
- Testsequence parsing.
- `NoteEvent` en `NoteSequence`.
- Sine/saw/square oscillator basis.
- Stereo/left/right channel routing.
- WAV writer.
- Audio device discovery and `--audio-device` selection.
- Optional realtime playback via `sounddevice`.
- Optional MIDI device discovery via `mido`.
- Pytest test skeleton.

Out of scope voor Sprint 1:

- GUI.
- VST3.
- Logic AU.
- MIDI performance workflow.
- Standalone macOS/Windows packaging.
- CircuitPython/ESP32 fork.
