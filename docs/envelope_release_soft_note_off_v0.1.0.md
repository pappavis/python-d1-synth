# CHATOD-20260709-D1PY-MVP-001 / US-040 Envelope Release / Soft Note-Off

- Sprintnummer: Future MIDI/DAW
- Doc versie: 0.1.0
- Status: Done
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-040 Envelope Release / Soft Note-Off
- Actie: US-040-RED-GREEN-001

## Doel

US-040 verzacht het einde van sustained notes. In plaats van een voice direct hard te stoppen bij `note_off`, krijgt de voice een korte release envelope. Daardoor klinkt note-off minder abrupt en is de synth beter speelbaar via Logic, MIDI keyboard en de bestaande commandline performance mode.

Product Owner acceptatie op 2026-07-12: US-040 is na push geaccepteerd.

## Gedrag

- Alleen `--voice-mode sustained` gebruikt de release envelope.
- Default release-tijd is `--release-time 0.03`.
- `--release-time 0` schakelt terug naar hard-stop gedrag voor technische vergelijking.
- CC64 sustain pedal blijft leidend: als sustain down is, start release pas wanneer de voice werkelijk wordt losgelaten.
- Pitch bend en CC1 modulation blijven actief op sustained voices totdat de release uitklinkt.
- Verbose output toont `release_time=<waarde>s`.

## Acceptatietest

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 10000 --max-control-messages 20000 --timeout 600 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --modulation-vibrato-depth 0.25 --modulation-vibrato-rate 5 --release-time 0.03 --until-interrupt --debuglevel verbose
```

Vergelijk met harde note-off:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 10000 --max-control-messages 20000 --timeout 600 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --modulation-vibrato-depth 0.25 --modulation-vibrato-rate 5 --release-time 0 --until-interrupt --debuglevel light
```

Verwacht:

- Notes stoppen hoorbaar zachter met `--release-time 0.03` dan met `--release-time 0`.
- Triads blijven speelbaar.
- Pitch bend en CC1 modulation blijven bruikbaar tijdens de sustained voice lifecycle.
- `Ctrl-C` stopt de performance-run zonder hang.

## Scopegrenzen

- Geen volledige ADSR envelope.
- Geen filter envelope.
- Geen velocity-afhankelijke release curves.
- Geen GUI.
- Geen AU/VST3/plugin packaging.
- Geen hardcoded MIDI hardware device names.

## Traceability

- ChatID: CHATOD-20260709-D1PY-MVP-001 / US-040
- Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-040 Envelope Release / Soft Note-Off
- Version: 0.1.0
