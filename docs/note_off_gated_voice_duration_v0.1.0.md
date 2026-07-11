# US-033 Note Off Gated Voice Duration

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-033
Sprintnummer: Future MIDI/DAW
Doc versie: 0.1.0
Epic: EPIC-007 Future MIDI En DAW Integratie
Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
Status: In Review

## Doel

US-033 voegt een gated voice duration mode toe aan `midi play-stream`, zodat `note_on` direct hoorbaar blijft en `note_off` de gerapporteerde nootlengte bepaalt. Hiermee verlaten we de pure fixed-duration diagnostics uit US-031/US-032 zonder meteen polyfonie, pitch bend, modulation of een echte low-latency sustain-engine te implementeren.

## Implementatie

- `StreamingVoiceMode` introduceert `fixed` en `gated`.
- `StreamingMidiAudioTriggerSettings.voice_mode` kiest de streaming voice-mode.
- `--voice-mode fixed` blijft de default en behoudt US-031/US-032 gedrag.
- `--voice-mode gated` bewaart actieve note-on messages per MIDI key: channel en note number.
- Bij `note_on` speelt de synth direct een korte hoorbare fallback-buffer, zodat live spelen niet stil lijkt.
- Een `note_off` of `note_on` met velocity `0` sluit de actieve noot en werkt `NoteEvent.duration_seconds` bij voor verbose diagnostics.
- Als een note-off ontbreekt binnen de bounded run, blijft `--note-duration` als fallback duration gebruikt.
- Duplicate MIDI events blijven via US-032 `--dedupe-window` gefilterd.

Scopegrenzen:

- Geen sustain pedal.
- Geen envelope release.
- Geen echte held/sustained audio tussen note-on en note-off; dat vereist een latere low-latency voice engine.
- Geen polyphonic voice mixer of triads; dat is US-034.
- Geen MIDI pitch bend; dat is US-035.
- Geen MIDI modulation/CC1; dat is US-036.
- Geen GUI, AU/VST3, Logic Component of plugin.
- Geen hardcoded MIDI hardware device names.

## Product Owner Acceptatietest

Start de synth:

```bash
cd /Volumes/data1/Yandex.Disk.localized/michiele/Programmering/Python/python_normaal/github_python_normaal/desktop_synth
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 30 --note-duration 0.25 --voice-mode gated --dedupe-window 0.03 --debuglevel verbose
```

Logic Pro test:

1. Gebruik een External MIDI track met MIDI Destination `python-d1-synth`.
2. Kies MIDI Channel `All` of channel `1`.
3. Maak een MIDI region met duidelijk korte en lange noten, bijvoorbeeld C4 kort, D4 lang, E4 kort.
4. Speel de region af terwijl het command draait.
5. Herhaal eventueel met live gespeelde noten op je MIDI keyboard.

Verwachte CLI-indicaties:

```text
Gated MVP note: note_on plays an audible fallback buffer and note_off reports duration
Streaming MIDI audio trigger settings: ... voice_mode=gated ...
Streamed note durations: C4@.../...s, D4@.../...s
```

Acceptatie:

- Korte en lange noten tonen verschillende durations in `Streamed note durations`.
- Er is hoorbaar geluid via `Scarlett 8i6 USB`.
- Duplicate MIDI messages worden nog steeds onderdrukt.
- Ctrl-C stopt de commandline met een interruptmelding.
- Eventuele kleine latency is toegestaan binnen US-033; low-latency voice mixing blijft later werk.

## Traceability

- Code: `src/synth/midi.py`, `src/synth/cli.py`
- Tests: `tests/test_midi.py`, `tests/test_cli.py`, `tests/test_traceability.py`, `tests/test_docs.py`
- User story: `docs/user_stories.md`
- Acceptatiecriteria: `docs/acceptance_criteria.md`
- Kanban: `outputs/CHATOD-20260709-D1PY-MVP-001/sprint1_kanban.xlsx`
