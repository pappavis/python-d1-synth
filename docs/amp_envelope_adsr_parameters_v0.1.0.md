# CHATOD-20260709-D1PY-MVP-001 / US-041 Amp Envelope ADSR Parameters

- Sprintnummer: Future MIDI/DAW
- Doc versie: 0.1.0
- Status: In Review
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-041 Amp Envelope ADSR Parameters
- Actie: US-041-RED-GREEN-001

## Doel

US-041 voegt amplitude ADSR parameters toe aan sustained playback. Daarmee kan de speler de start, decay, hold-level en release van sustained voices instellen zonder de scope uit te breiden naar filter envelopes, GUI of plugin packaging.

## Gedrag

- Alleen `--voice-mode sustained` gebruikt de ADSR amplitude envelope.
- `--attack-time` bepaalt hoe snel de amplitude vanaf note-on naar vol niveau groeit.
- `--decay-time` bepaalt hoe snel de amplitude na attack naar `--sustain-level` beweegt.
- `--sustain-level` ligt tussen `0.0` en `1.0`.
- `--release-time` blijft de note-off/release fade bepalen en start vanaf het actuele ADSR-level.
- Default blijft compatibel met US-040: `--attack-time 0`, `--decay-time 0`, `--sustain-level 1`, `--release-time 0.03`.

## Acceptatietest

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 10000 --max-control-messages 20000 --timeout 600 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --modulation-vibrato-depth 0.25 --modulation-vibrato-rate 5 --attack-time 0.02 --decay-time 0.12 --sustain-level 0.6 --release-time 0.08 --until-interrupt --debuglevel verbose
```

Verwacht:

- Notes hebben een hoorbaar zachtere attack dan `--attack-time 0`.
- Na de attack zakt het niveau richting `--sustain-level 0.6`.
- Note-off klinkt uit met `--release-time 0.08`.
- Verbose output bevat `attack_time=0.02s`, `decay_time=0.12s`, `sustain_level=0.6` en `release_time=0.08s`.
- Pitch bend, CC1 modulation, CC64 sustain pedal en `Ctrl-C` cleanup blijven werken.

## Scopegrenzen

- Geen filter envelope.
- Geen velocity-afhankelijke envelope curves.
- Geen per-patch YAML envelope in deze story.
- Geen GUI.
- Geen AU/VST3/plugin packaging.
- Geen hardcoded MIDI hardware device names.

## Traceability

- ChatID: CHATOD-20260709-D1PY-MVP-001 / US-041
- Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-041 Amp Envelope ADSR Parameters
- Version: 0.1.0
