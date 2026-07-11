# US-032 Duplicate MIDI Event Guard

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-032  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Epic: EPIC-007 Future MIDI En DAW Integratie  
Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog  
Status: Done

## Doel

US-032 voorkomt dat Logic Pro 12.3, CoreMIDI of een routingconfiguratie identieke duplicate MIDI events twee keer hoorbaar afspeelt via `midi play-stream`.

De guard is klein gehouden: hij onderdrukt alleen identieke `MidiMessage` waarden binnen een korte dedupe-window. Ook geldt: verschillende note numbers op dezelfde timestamp blijven behouden, zodat toekomstige polyfonie/triads in US-034 niet door deze story worden geblokkeerd.

## Implementatie

- `DuplicateMidiEventGuardSettings` configureert de `window_seconds`.
- `DuplicateMidiEventGuard` onthoudt de laatste tijd per MIDI key: message type, note number, velocity en channel.
- `StreamingMidiAudioTriggerSettings` heeft `dedupe_window_seconds`.
- `StreamingMidiAudioTriggerResult` rapporteert `suppressed_duplicate_count`.
- `midi play-stream` heeft de CLI optie `--dedupe-window`.

Scopegrenzen:

- Geen note-off gated voice duration; dat is US-033.
- Geen polyphonic voice mixer; dat is US-034.
- Geen pitch bend; dat is US-035.
- Geen modulation/CC1; dat is US-036.
- geen GUI, AU/VST3 of Logic Component.
- geen hardcoded MIDI hardware device names.

## Testcommand Voor Product Owner

```bash
cd /Volumes/data1/Yandex.Disk.localized/michiele/Programmering/Python/python_normaal/github_python_normaal/desktop_synth
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 30 --note-duration 0.25 --dedupe-window 0.03 --debuglevel verbose
```

Logic Pro test:

1. Start bovenstaande command.
2. Maak of gebruik een External MIDI track met MIDI Destination `python-d1-synth`.
3. Kies MIDI Channel `All` of channel `1`.
4. Speel dezelfde MIDI region af als in US-031.
5. Controleer dat een enkele notenlijn niet meer dubbel klinkt door identieke echo-events.

Verwachte CLI-indicaties:

```text
Streaming MIDI audio trigger settings: ... dedupe_window=0.03s ...
Streamed ... MIDI-triggered note events from virtual MIDI port python-d1-synth; suppressed ... duplicate MIDI messages.
Suppressed duplicate MIDI messages: ...
```

## Acceptatiecriteria

- Identieke duplicate `note_on` messages binnen de window worden niet twee keer afgespeeld.
- Identieke duplicate `note_off` messages binnen de window worden diagnostisch onderdrukt.
- Verschillende simultane noten worden niet onderdrukt.
- Verbose output toont ontvangen MIDI messages, streamed sequence events en het aantal onderdrukte duplicates.
- Tests draaien groen met `pytest`.

## Product Owner Testresultaat

Datum: 2026-07-11
Host: KodeklopperM4
Audio device: Scarlett 8i6 USB
DAW: Logic Pro 12.3
Beoordeling: geslaagd

De Product Owner bevestigde hoorbaar geluid vanuit Logic en live note playback. Er bleef een kleine vertraging merkbaar; dat is geen US-032 blocker en hoort bij latere latency/voice-lifecycle stories.

Belangrijkste CLI-resultaten:

```text
Streamed 6 MIDI-triggered note events from virtual MIDI port python-d1-synth; suppressed 23 duplicate MIDI messages.
Suppressed duplicate MIDI messages: 23
Streamed sequence events: A4@0.721s, F4@0.721s, G4@0.721s, A4@0.721s, G4@0.721s, F4@0.721s
```

US-032 status: `Done`.

## Traceability

- Code: `src/synth/midi.py`, `src/synth/cli.py`
- Tests: `tests/test_midi.py`, `tests/test_cli.py`, `tests/test_traceability.py`, `tests/test_docs.py`
- User story: `docs/user_stories.md`
- Acceptatiecriteria: `docs/acceptance_criteria.md`
- Kanban: `outputs/CHATOD-20260709-D1PY-MVP-001/sprint1_kanban.xlsx`
