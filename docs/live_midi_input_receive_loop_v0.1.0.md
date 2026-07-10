# Live MIDI Input Receive Loop

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-026-LIVE-MIDI-RECEIVE-001  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Status: Done  
User Story: US-026 Live MIDI Input Receive Loop  
Epic: EPIC-007 Future MIDI En DAW Integratie  
Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog  
Datum: 2026-07-10

## Doel

US-026 voegt een bounded live MIDI input receive loop toe. De commandline kan een MIDI input selecteren, een beperkt aantal note messages ontvangen, deze normaliseren naar `MidiMessage`, en daarna via US-024 mappen naar `NoteSequence`.

Belangrijk voor de implementatievolgorde:

- Dit is geen Logic virtual device story.
- Dit is geen realtime audio-trigger story.
- Dit is geen VST3, Audio Unit of USB driver story.
- Hardwaretest pauzeert bij klant voordat we echte devices zoals MidiportA of SMK 37 Pro BLE gebruiken.
- Auditregel: hardwaretest pauzeert bij klant.

## Runtime Klassen

- `MidiInputReceiveSettings`: inputnaam, maximaal aantal berichten en timeout.
- `MidiInputReceiveResult`: ontvangen `MidiMessage` items, gemapte `NoteSequence` en statusmelding.
- `MidiMessageNormalizer`: normaliseert backend-specifieke note messages naar project `MidiMessage`.
- `MidoMidiInputBackend`: bounded adapter rond een mido input port voor toekomstige hardwaretests.
- `LiveMidiInputReceiver`: orchestratieklasse die backend messages ontvangt en naar `NoteSequence` mapt.

## Commandline

De nieuwe commandline route is:

```bash
PYTHONPATH=src python -m synth midi listen --unsafe-rtmidi-scan --midi-device "deel van input device naam" --max-messages 10 --timeout 5 --debuglevel light
```

Of via identifier:

```bash
PYTHONPATH=src python -m synth midi listen --unsafe-rtmidi-scan --midi-device-id "input:0" --max-messages 10 --timeout 5 --debuglevel light
```

Of via YAML default:

```bash
PYTHONPATH=src python -m synth midi listen --unsafe-rtmidi-scan --config patch.yaml --max-messages 10 --timeout 5 --debuglevel light
```

## Testvolgorde Voor Hardware

Wanneer we later handmatig testen, volgen we deze volgorde:

1. Scan eerst met `midi list-devices --unsafe-rtmidi-scan`.
2. Kies een input device met `--midi-device-id` of `--midi-device`.
3. Start `midi listen`.
4. Speel enkele noten op het gekozen device.
5. Leg command, hostnaam, device, datum en output vast.

Voorbeelden van mogelijke klantdevices zijn `MidiportA`, `SMK 37 Pro BLE`, KeyLab, Fishman TriplePlay of een class-compliant USB MIDI interface. Deze namen zijn alleen testcontext; geen hardcoded MIDI device names in runtime code.

## Scope Grenzen

US-026 ontvangt en mapt note messages. Het speelt nog geen geluid af.

Bewust buiten scope:

- geen Logic virtual device;
- geen external MIDI track destination in Logic;
- geen realtime audio-trigger;
- geen MIDI clock, pitch bend, aftertouch of control change verwerking;
- geen langdurige performance loop zonder timeout.

## Red/Green Tests

Red phase:

- Imports faalden zolang `LiveMidiInputReceiver`, `MidiInputReceiveSettings`, `MidiInputReceiveResult` en `MidiMessageNormalizer` ontbraken.
- CLI-test faalde zolang `midi listen` nog niet bestond.

Green phase:

- `MidiMessageNormalizer` vertaalt een mido-achtige `note_on` naar `MidiMessage`.
- Mido channel `0` wordt intern channel `1`.
- Niet-note messages worden genegeerd voor US-026.
- `LiveMidiInputReceiver` gebruikt een fake backend en mapt ontvangen messages naar `NoteSequence`.
- CLI `midi listen` werkt met fake scanner en fake backend zonder hardware.

## Acceptatie

- De receive-loop is bounded met `--max-messages` en `--timeout`.
- De commandline selecteert input via bestaande US-025 selectie.
- Ontvangen note messages worden als `MidiMessage` opgeslagen.
- US-024 mapping wordt hergebruikt voor `NoteSequence`.
- Tests gebruiken een fake backend.
- Echte hardwaretest wordt pas uitgevoerd na expliciete klantactie.

## Hardwaretest KodeklopperM4

CHATOD: CHATOD-20260709-D1PY-MVP-001 / US-026-HARDWARE-TESTRESULT
Datum: 2026-07-10
Host: KodeklopperM4
Status: Geslaagd

De klant heeft `midi listen` getest met `SMK-37 Pro_BLE Bluetooth`.

Test via naamfragment:

```bash
PYTHONPATH=src python -m synth midi listen --unsafe-rtmidi-scan --midi-device "MK-37 Pro_BLE" --max-messages 10 --timeout 5 --debuglevel light
```

Resultaat:

```text
Selected MIDI input device from cli: input:7 SMK-37 Pro_BLE Bluetooth
Received 10 MIDI note messages from SMK-37 Pro_BLE Bluetooth.
Received sequence: B4@0.000s, G4@0.000s, B4@0.000s, A4@0.000s, G4@0.000s, B4@0.000s
```

Device scan bevatte onder meer:

```text
input:7 input   SMK-37 Pro_BLE Bluetooth
input:8 input   SN76489 Synth Pappavis CircuitPython usb_midi.ports[0]
input:9 input   Logic Pro Virtual Out
output:10       output  Logic Pro Virtual In
```

Test via identifier:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi listen --unsafe-rtmidi-scan --midi-device-id "input:7" --max-messages 4 --timeout 10 --debuglevel light
```

Resultaat:

```text
Selected MIDI input device from cli-id: input:7 SMK-37 Pro_BLE Bluetooth
Received 4 MIDI note messages from SMK-37 Pro_BLE Bluetooth.
Received sequence: C5@0.000s, B3@0.000s, B4@0.000s, A3@0.000s
```

Conclusie: US-026 is hardwarematig geslaagd op KodeklopperM4. De app ontvangt echte MIDI note messages van een geselecteerde input en mapt deze naar een `NoteSequence`. Hoorbare audio-triggering blijft bewust buiten US-026 en hoort bij US-028.
