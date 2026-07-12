# CHATOD-20260709-D1PY-MVP-001 / US-038 Performance Mode Until Interrupt

- Sprintnummer: Future MIDI/DAW
- Doc versie: 0.1.0
- Status: In Review
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-038 Performance Mode Until Interrupt
- Actie: US-038-RED-GREEN-001

## Doel

US-038 maakt `midi play-stream` bruikbaar als eenvoudige performance-run: de gebruiker kan de Python D1 synth starten, in Logic/DAW of op een MIDI keyboard spelen, en de sessie stoppen met `Ctrl-C`.

## Gedrag

- CLI optie: `--until-interrupt`.
- Runtime gebruikt praktische lange backend-limieten in plaats van de normale bounded `--max-messages` en `--timeout` stopvoorwaarden.
- De bestaande Ctrl-C route blijft actief en rapporteert `Streaming MIDI audio trigger interrupted by user.`.
- `--debuglevel verbose` toont `until_interrupt=true`.

## Acceptatietest

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 10000 --max-control-messages 20000 --timeout 600 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --modulation-vibrato-depth 0.25 --modulation-vibrato-rate 5 --until-interrupt --debuglevel verbose
```

Verwacht:

- `Performance mode: running until Ctrl-C`
- `until_interrupt=true`
- hoorbare sustained notes, triads, pitch bend en CC1 modulation zoals US-035 t/m US-037
- `Ctrl-C` stopt de sessie zonder hang

## Scopegrenzen

- Geen sustain pedal.
- Geen envelope release.
- Geen GUI.
- Geen AU/VST3/plugin packaging.
- Geen hardcoded MIDI hardware device names.

## Traceability

- ChatID: CHATOD-20260709-D1PY-MVP-001 / US-038
- Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-038 Performance Mode Until Interrupt
- Version: 0.1.0
