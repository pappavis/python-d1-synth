# CHATOD-20260709-D1PY-MVP-001 / US-039 Sustain Pedal CC64

- Sprintnummer: Future MIDI/DAW
- Doc versie: 0.1.0
- Status: Done
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-039 Sustain Pedal CC64
- Actie: US-039-RED-GREEN-001

## Doel

US-039 voegt MIDI sustain pedal ondersteuning toe aan sustained playback. CC64 is de MIDI sustain controller: waarden `64..127` betekenen pedal down en waarden `0..63` betekenen pedal up.

Product Owner acceptatie op 2026-07-12: er is geen fysieke sustain pedal beschikbaar; US-039 is geaccepteerd op basis van aanname plus groene automatische CC64-tests.

## Gedrag

- Alleen `--voice-mode sustained` past CC64 muzikaal toe.
- `control_change:64:<waarde>:channel=<n>` wordt in verbose output zichtbaar.
- Bij pedal down blijft een voice klinken wanneer de fysieke toets een `note_off` stuurt.
- Bij pedal up worden de door sustain vastgehouden voices op dat MIDI channel losgelaten.
- De bestaande pitch bend, CC1 modulation, duplicate guard en `--until-interrupt` performance mode blijven werken.

## Acceptatietest

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 10000 --max-control-messages 20000 --timeout 600 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --modulation-vibrato-depth 0.25 --modulation-vibrato-rate 5 --until-interrupt --debuglevel verbose
```

Handmatige test:

1. Houd sustain pedal ingedrukt.
2. Speel een noot of triad.
3. Laat de toetsen los terwijl pedal nog ingedrukt blijft.
4. Laat de sustain pedal los.

Verwacht:

- Notes blijven hoorbaar nadat de toetsen losgelaten zijn.
- Notes stoppen wanneer de sustain pedal losgelaten wordt.
- Verbose output bevat `control_change:64:127:channel=<n>` en `control_change:64:0:channel=<n>`.
- `Ctrl-C` stopt de performance-run zonder hang.

## Scopegrenzen

- Geen half-pedal curves.
- Geen envelope release.
- Geen sostenuto pedal.
- Geen GUI.
- Geen AU/VST3/plugin packaging.
- Geen hardcoded MIDI hardware device names.

## Traceability

- ChatID: CHATOD-20260709-D1PY-MVP-001 / US-039
- Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-039 Sustain Pedal CC64
- Version: 0.1.0
