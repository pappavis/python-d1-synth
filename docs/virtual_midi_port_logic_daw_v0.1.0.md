# US-027 Virtual MIDI Port Voor Logic/DAW

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-027-VIRTUAL-MIDI-PORT-001  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Epic: EPIC-007 Future MIDI En DAW Integratie  
User Story: US-027 Virtual MIDI Port Voor Logic/DAW  
Status: In Review  

## Doel

US-027 voegt een bounded virtual MIDI port workflow toe waarmee `python-d1-synth` als virtual MIDI destination zichtbaar kan worden voor Logic Pro 12.3 of een andere DAW. Dit is nog geen realtime audio-trigger. De ontvangen MIDI naar hoorbare synth-audio koppeling blijft bewust in US-028.

## Scope

- CLI command: `midi virtual-port`.
- Default port name: `python-d1-synth`.
- Bounded lifecycle via `--timeout`, zodat een test niet oneindig blijft hangen.
- Backenddiagnose met duidelijke foutmelding als mido/python-rtmidi/CoreMIDI geen virtual input port kan openen.
- Unit tests met fake backend; geen automatische test opent een echte CoreMIDI-port.
- Geen hardcoded MIDI device names. Namen uit KodeklopperM4, MuziekM4, Spelen01 of Raspberry Pi 2 blijven runtime testdata.

## Implementatie

Nieuwe code-objecten:

- `VirtualMidiPortSettings`: bewaart port name en timeout.
- `VirtualMidiPortResult`: beschrijft of de virtual MIDI input port is geopend.
- `MidoVirtualMidiPortBackend`: gebruikt `mido.open_input(name, virtual=True)` voor de echte DAW-zichtbaarheidstest.
- `VirtualMidiPortManager`: class-based lifecycle wrapper rond de backend.

De commandline route staat bewust los van `midi listen`. US-027 bewijst eerst dat de port kan verschijnen in Logic/DAW; US-028 koppelt daarna live MIDI receive aan audio-output.

## CLI Gebruik

Start de virtual MIDI port en laat het command open terwijl Logic Pro wordt gecontroleerd:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi virtual-port --name python-d1-synth --timeout 60 --debuglevel light
```

Verwacht bij succesvolle opening:

```text
Opening virtual MIDI input port: python-d1-synth
Keep this command running while you check Logic Pro or another DAW for the virtual MIDI destination.
Virtual MIDI input port opened: python-d1-synth.
```

Let op: door de bounded timeout verschijnt de laatste regel pas nadat de port weer gesloten is. Controleer Logic Pro dus terwijl het command nog draait.

## Handmatige Logic Test

1. Sluit onnodige MIDI testcommands.
2. Start `midi virtual-port` met `--timeout 60` of langer.
3. Open Logic Pro 12.3.
4. Maak of open een project met een External MIDI track.
5. Controleer de MIDI destination lijst.
6. Kijk of `python-d1-synth` als virtual MIDI destination verschijnt.
7. Noteer of de destination zichtbaar is en of Logic Pro foutmeldingen toont.
8. Stuur het terminalresultaat en je Logic-observatie terug naar de backlog.

hardware/Logic test pauzeert bij klant: deze story blijft `In Review` totdat de Logic-zichtbaarheid is bevestigd of als blocker is vastgelegd.

## Teststrategie

Rode fase:

- Importtests faalden zolang `VirtualMidiPortSettings`, `VirtualMidiPortResult` en `VirtualMidiPortManager` ontbraken.
- CLI-test faalde zolang `midi virtual-port` niet bestond.

Groene fase:

- `VirtualMidiPortManager` gebruikt een fake backend in unit tests.
- CLI-test verifieert dat `--name python-d1-synth` en `--timeout 0.5` naar de manager gaan.
- CLI-test verifieert dat backendfouten als duidelijke `Virtual MIDI port error` worden gemeld.
- Traceability-tests verifieren ChatOD, backlog, epic, `US-027 Virtual MIDI Port Voor Logic/DAW` en `Version: 0.1.0`.
- Docs-test verifieert dit artefact.

## Acceptatie

- `midi virtual-port` bestaat en is bounded via `--timeout`.
- `VirtualMidiPortSettings`, `VirtualMidiPortResult`, `MidoVirtualMidiPortBackend` en `VirtualMidiPortManager` zijn class-based en traceerbaar.
- Automatische tests openen geen echte CoreMIDI-port.
- De story bevat geen realtime audio-trigger en verwijst dat bewust naar US-028.
- Er zijn geen hardcoded MIDI device names toegevoegd.
- Logic Pro 12.3 handmatige test moet nog klantmatig worden uitgevoerd.
