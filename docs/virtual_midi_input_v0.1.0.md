# Virtual MIDI Input Voor DAW

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-020-VIRTUAL-MIDI-001  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Datum: 2026-07-09  
User Story: US-020 Virtual MIDI Input Voor DAW  
Epic: EPIC-007 Future MIDI En DAW Integratie

## Doel

US-020 legt de eerste veilige software-route vast waarmee een DAW, zoals Logic Pro 12.3, later MIDI note events naar `python-d1-synth` kan sturen. Deze story opent nog geen live CoreMIDI/RtMidi poort; dat blijft bewust gescheiden omdat eerdere macOS crashrapporten lieten zien dat native MIDI-scans hard kunnen aborten.

## Wat Nu Werkt

- `MidiMessage` normaliseert MIDI `note_on` en `note_off` data.
- `VirtualMidiInputAdapter` vertaalt note-on/off paren naar het interne `NoteSequence` model.
- Een `note_on` met velocity `0` wordt behandeld als `note_off`, zoals veel MIDI-apparaten doen.
- Velocity wordt genormaliseerd van `0..127` naar `0.0..1.0` voor `NoteEvent.velocity`.
- MIDI note number wordt vertaald naar dezelfde noot/frequentie-basis als `NoteParser`.
- De CLI heeft een diagnosecommando:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi diagnose-virtual-input
```

## Voorbeeld Mapping

| MIDI bericht | Betekenis | Interne output |
| --- | --- | --- |
| `note_on`, note number 60, velocity 96, channel 1, tijd 0.25 | C4 start | `NoteEvent(note=C4, velocity=96/127, start_seconds=0.25)` |
| `note_off`, note number 60, velocity 0, channel 1, tijd 0.75 | C4 stopt | `duration_seconds=0.5` |
| `note_on`, note number 64, velocity 0 | Note-off variant | Sluit actieve E4 af |

## Platformdiagnose

Het diagnosecommando controleert alleen of de Python MIDI-backend zichtbaar is. Het opent nog geen live virtual MIDI port. Dat is met opzet:

- veilig in Codex en CI;
- geen CoreMIDI/RtMidi crashroute tijdens documentatie- of testwerk;
- klaar om later in US-021/US-022/US-025 aan echte DAW- en hardwaretests gekoppeld te worden.

## Acceptatie

- Logic Pro 12.3 en andere DAWs hebben een gedefinieerde software-route richting een toekomstige virtual MIDI input.
- MIDI note on/off data wordt testbaar vertaald naar `NoteSequence` en `NoteEvent`.
- Als de backend niet beschikbaar is, geeft de CLI een duidelijke diagnose.
- Code bevat traceability voor ChatOD, backlog, epic, user story en versie.
