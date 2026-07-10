# US-028 External MIDI Audio Trigger Integratie

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-028-EXTERNAL-MIDI-AUDIO-001
Sprintnummer: Future MIDI/DAW
Doc versie: 0.1.0
Epic: EPIC-007 Future MIDI En DAW Integratie
User Story: US-028 External MIDI Audio Trigger Integratie
Status: In Review

## Doel

US-028 koppelt de bounded MIDI receive workflow aan de bestaande synth-engine en audio-output. De gebruiker kiest een MIDI input device en optioneel een audio-output device; ontvangen note events worden naar `NoteSequence` gemapt, met `SynthEngine` gerenderd, en via `SoundDeviceAudioPlayer` afgespeeld.

Dit is bewust nog geen GUI, geen plugin, geen Audio Unit, geen VST3 en geen onbeperkte realtime performance-loop. Het is de eerste hoorbare MIDI-audio integratie voor de commandline MVP.

## Implementatie

Nieuwe code-objecten:

- `MidiAudioTriggerSettings`: input device, max messages, timeout, waveform, sample rate, channel en audio device.
- `MidiAudioTriggerResult`: aantallen ontvangen MIDI messages, gespeelde events en audio frames.
- `MidiAudioTrigger`: ontvangt bounded MIDI via `LiveMidiInputReceiver`, rendert via `SynthEngine`, en speelt via `SoundDeviceAudioPlayer`.

CLI command:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-live --unsafe-rtmidi-scan --midi-device-id "input:7" --audio-device "Scarlett 8i6 USB" --max-messages 10 --timeout 10 --debuglevel light
```

Alternatief met naamfragment:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-live --unsafe-rtmidi-scan --midi-device "SMK-37 Pro_BLE" --audio-device "Scarlett 8i6 USB" --max-messages 10 --timeout 10 --debuglevel light
```

## Teststrategie

Rode fase:

- `MidiAudioTriggerSettings`, `MidiAudioTriggerResult` en `MidiAudioTrigger` ontbraken.
- CLI command `midi play-live` ontbrak.

Groene fase:

- Unit tests gebruiken een fake MIDI backend / fake receiver en fake audio player.
- CLI tests gebruiken fake MIDI device discovery, fake audio selection en fake trigger.
- Er wordt geen echte MIDI hardware en geen echte audio-output geopend in automatische tests.
- `midi play-live` gebruikt dezelfde runtime device discovery als US-025 en US-026.

## Handmatige Hardwaretest

US-028-HARDWARE-TEST

hardwaretest pauzeert bij klant: de automatische tests zijn groen, maar de story blijft `In Review` totdat de gebruiker hoorbaar resultaat bevestigt.

Voor de test:

1. Start met device discovery:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi list-devices --unsafe-rtmidi-scan --debuglevel light
```

2. Kies een MIDI input, bijvoorbeeld `SMK-37 Pro_BLE`, Logic Pro Virtual Out, of een andere zichtbare input.
3. Kies een audio-output, bijvoorbeeld `Scarlett 8i6 USB` of Mac mini luidsprekers.
4. Draai `midi play-live`.
5. Speel een paar noten op het gekozen MIDI device binnen de timeout.
6. Rapporteer of er hoorbaar geluid kwam, welk MIDI input device is gekozen en welk audio-output device is gebruikt.

Voorbeeld:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-live --unsafe-rtmidi-scan --midi-device "SMK-37 Pro_BLE" --audio-device "Scarlett 8i6 USB" --max-messages 10 --timeout 10 --debuglevel verbose
```

## Scopebewaking

- geen hardcoded MIDI device names in applicatiecode.
- Device-namen zoals `Scarlett 8i6 USB` en `SMK-37 Pro_BLE` zijn testvoorbeelden, geen constants.
- Geen GUI.
- Geen plugin.
- Geen onbeperkte realtime performance-loop.
- Geen latency-optimalisatie buiten bounded commandline test.
- Geen AU/VST3/Logic Component.

## Acceptatie

- `midi play-live` bestaat.
- Een geselecteerde MIDI input wordt via runtime discovery gekozen.
- Ontvangen note messages worden via de bestaande mapper naar `NoteSequence` vertaald.
- `MidiAudioTrigger` rendert audio met `SynthEngine`.
- Audio wordt via de gekozen output afgespeeld.
- Tests gebruiken fake MIDI backend en fake audio player.
- Story status blijft `In Review` tot de hardwaretest hoorbaar geslaagd is.
