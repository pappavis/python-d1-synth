# MIDI Device Discovery En Default Selection

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-025-MIDI-DEVICE-SELECTION-001  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Status: Done  
User Story: US-025 MIDI Device Discovery En Default Selection  
Epic: EPIC-007 Future MIDI En DAW Integratie  
Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog  
Datum: 2026-07-10

## Doel

US-025 maakt MIDI device discovery en bewuste input-selectie reproduceerbaar. De CLI kan MIDI devices tonen en een input-device kiezen via commandline of YAML config. Dit is voorbereiding voor latere live MIDI receive; deze story opent nog geen realtime MIDI inputpoort voor audio-triggering.

## Runtime Klassen

- `MidiDeviceScanner`: voert veilige discovery uit en houdt native RtMidi/CoreMIDI scanning op macOS standaard uit.
- `MidiDeviceSelector`: kiest een input-device op basis van `--midi-device-id`, `--midi-device` of YAML default.
- `MidiDeviceSelection`: bewaart de gekozen bron, request-string, resolved runtime device en gebruikersmelding.

## Selectievolgorde

CLI wint van YAML:

1. `--midi-device-id` wint altijd.
2. `--midi-device` wint van YAML.
3. `midi.default_input_device` uit `--config patch.yaml` wordt gebruikt wanneer er geen CLI override is.
4. Zonder keuze wordt alleen de device-lijst getoond.

## Commands

Veilige default scan:

```bash
PYTHONPATH=src python -m synth midi list-devices --debuglevel light
```

Bewuste native backenddiagnose:

```bash
PYTHONPATH=src python -m synth midi list-devices --unsafe-rtmidi-scan --debuglevel light
```

Kies een input-device via naam:

```bash
PYTHONPATH=src python -m synth midi list-devices --unsafe-rtmidi-scan --midi-device "deel van device naam" --debuglevel light
```

Kies een input-device via identifier:

```bash
PYTHONPATH=src python -m synth midi list-devices --unsafe-rtmidi-scan --midi-device-id "input:0" --debuglevel light
```

Kies een default uit YAML:

```yaml
midi:
  default_input_device: "deel van device naam"
```

```bash
PYTHONPATH=src python -m synth midi list-devices --unsafe-rtmidi-scan --config patch.yaml --debuglevel light
```

## Testprocedure Per Computer

Gebruik deze volgorde op KodeklopperM4, MuziekM4, toekomstig Windows Spelen01 of Raspberry Pi 2:

1. Run `midi list-devices`.
2. Controleer welke devices als `input` zichtbaar zijn.
3. Kies een input via `--midi-device-id` of `--midi-device`.
4. Als de computer een vaste voorkeur heeft, zet die voorkeur in YAML als `midi.default_input_device`.
5. Leg het testresultaat vast met hostnaam, datum, command en output.

## Ontwerpregels

- Geen hardcoded MIDI device names in runtime code.
- Review-afspraak: geen hardcoded MIDI device names toevoegen aan applicatiecode.
- Device-namen uit KodeklopperM4, MuziekM4, Spelen01 of Raspberry Pi 2 zijn alleen snapshots/testdata.
- De applicatie moet op willekeurige computers kunnen draaien.
- De selector kijkt alleen naar runtime scanresultaten.
- Output devices worden niet als MIDI input geselecteerd.
- Op macOS blijft `--unsafe-rtmidi-scan` expliciet, omdat CoreMIDI/RtMidi in eerdere tests native aborts kon veroorzaken.

## Red/Green Tests

Red phase:

- Tests faalden op ontbrekende `select_input_device`.
- CLI-tests faalden op ontbrekende `--midi-device-id`, `--midi-device` en `--config` flags voor `midi list-devices`.

Green phase:

- `--midi-device-id` selecteert exact op input identifier.
- `--midi-device` selecteert op naamfragment of identifier.
- `midi.default_input_device` uit YAML werkt wanneer er geen CLI override is.
- CLI wint van YAML.
- Onbekende input geeft een duidelijke melding met beschikbare input devices en advies om `midi list-devices` opnieuw te draaien.

## Acceptatie

- `midi list-devices` toont `identifier`, `direction` en `name`.
- Selectie werkt via CLI naam, CLI identifier en YAML default.
- Foutmeldingen blijven leesbaar en crashen niet.
- De veilige macOS default blijft behouden.
- Docs, tests, traceability en Kanban backlog zijn bijgewerkt.
