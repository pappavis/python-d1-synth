# MIDI Naar NoteEvent Mapping

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-024-MIDI-NOTE-MAPPING-001  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Status: Done  
User Story: US-024 MIDI Naar NoteEvent Mapping  
Epic: EPIC-007 Future MIDI En DAW Integratie  
Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog  
Datum: 2026-07-10

## Doel

US-024 maakt een expliciete, device-onafhankelijke mapping van MIDI note messages naar het bestaande interne `NoteEvent` en `NoteSequence` model. Daardoor blijft de Sprint 1 synth-engine herbruikbaar voor toekomstige USB MIDI, virtual MIDI, external MIDI, Logic Pro, Windows, Raspberry Pi en CircuitPython routes.

Belangrijk: deze story opent nog geen live MIDI input poort en speelt nog geen realtime hardware-MIDI naar audio. Dat hoort bij een volgende user story.

## Implementatie

De code gebruikt `MidiToNoteEventMapper` in `src/synth/midi.py`.

Invoer:

- `MidiMessage(message_type="note_on", note_number=60, velocity=64, channel=1, time_seconds=0.1)`
- `MidiMessage(message_type="note_off", note_number=60, velocity=0, channel=1, time_seconds=0.6)`

Uitvoer:

- `NoteSequence` met een of meer `NoteEvent` items.
- MIDI note number 60 wordt `C4`.
- `velocity` wordt genormaliseerd naar `0.0` tot en met `1.0`.
- `start_seconds` komt uit het oorspronkelijke `note_on` bericht.
- `duration_seconds` komt uit het verschil tussen `note_off` en `note_on`.

## Mappingregels

| MIDI input | Interne interpretatie |
| --- | --- |
| `note_on` met velocity groter dan 0 | Start een actieve noot op `(channel, note_number)`. |
| `note_off` | Sluit de actieve noot op hetzelfde `(channel, note_number)`. |
| `note_on` met velocity 0 | Wordt behandeld als `note_off`, omdat veel MIDI-apparaten dit zo sturen. |
| Zelfde note number op verschillende channels | Wordt onafhankelijk gemapt; `channel` voorkomt dat events elkaar overschrijven. |
| Ontbrekende note-off | Gebruikt `default duration`, standaard 1.0 seconde of de ingestelde fallback. |

## Ontwerpkeuzes

- Geen hardcoded MIDI device names in runtime code.
- Afspraak voor reviews: geen hardcoded MIDI device names toevoegen aan applicatiecode.
- Device-namen uit KodeklopperM4, MuziekM4, Spelen01 of Raspberry Pi tests blijven snapshots/testdata.
- De mapper is class based en houdt state lokaal in methode-aanroepen.
- Pitch bend, MIDI clock, aftertouch en control change worden later als aparte stories toegevoegd.
- De bestaande `VirtualMidiInputAdapter` gebruikt dezelfde mapper zodat DAW-routes en hardware-routes niet elk hun eigen mappinglogica krijgen.

## Red/Green Tests

Red phase:

- `tests/test_midi.py` importeerde eerst `MidiToNoteEventMapper`, waardoor pytest faalde zolang de klasse ontbrak.

Green phase:

- `note_on` + `note_off` levert `C4`, correcte duration, velocity en starttijd.
- `note_on` met velocity 0 sluit een actieve note.
- Ontbrekende note-off gebruikt de ingestelde default duration.
- Hetzelfde note number op verschillende channels levert onafhankelijke `NoteEvent` items.
- Traceability-tests controleren ChatOD, backlog, epic, user story en versie.

## Acceptatie

- `MidiToNoteEventMapper` bestaat en is expliciet traceerbaar naar US-024.
- `MidiMessage` naar `NoteSequence` mapping werkt zonder gekoppeld te zijn aan een specifiek USB of DAW device.
- `VirtualMidiInputAdapter` hergebruikt de nieuwe mapper.
- Docs en Kanban backlog zijn bijgewerkt.
- `pytest` draait groen voor de automatische suite.
