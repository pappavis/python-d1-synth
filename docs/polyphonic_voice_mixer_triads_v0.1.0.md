# CHATOD-20260709-D1PY-MVP-001 / US-034 Polyphonic Voice Mixer En Triads

Sprintnummer: Future MIDI/DAW
Doc versie: 0.1.0
Epic: EPIC-007 Future MIDI En DAW Integratie
Status: Done

## Doel

US-034 voegt polyphonic voice mixing toe aan `midi play-stream`, zodat drie of meer gelijktijdige `note_on` events als triad/akkoordbuffer hoorbaar samen klinken. Dit bouwt bewust voort op US-032 duplicate filtering en US-033 gated duration reporting zonder pitch bend, modulation of een echte sustained voice engine te introduceren.

## Implementatie

- `PolyphonicVoiceMixer` mixt overlappende `NoteEvent` voices naar een mono buffer en routeert daarna via de bestaande stereo/left/right audio route.
- `MidoStreamingVirtualMidiInputBackend.iter_message_batches` levert alle MIDI messages uit een CoreMIDI poll als batch.
- `StreamingMidiAudioTrigger` gebruikt batch polling wanneer beschikbaar en valt terug naar single-message streaming voor bestaande test/fake backends.
- `StreamingMidiAudioTriggerSettings.chord_window_seconds` bepaalt welke note-on events als akkoordgroep worden behandeld.
- CLI optie: `--chord-window`, default `0.02`.
- Duplicate filtering blijft eerst actief, zodat identieke Logic/CoreMIDI echo-events worden onderdrukt maar verschillende chord tones behouden blijven.

Scopegrenzen:

- Geen echte held/sustained audio tussen note-on en note-off; dat blijft US-035.
- Geen MIDI pitch bend; dat blijft US-036.
- Geen MIDI modulation/CC1; dat blijft US-037.
- Geen GUI, AU, VST3 of Logic Component.
- Geen hardcoded MIDI hardware device names.

## Acceptatietest

Logic Pro test:

1. Start de commandline synth.
2. Selecteer in Logic `python-d1-synth` als External MIDI destination.
3. Speel of teken een triad, bijvoorbeeld C-E-G, op hetzelfde moment.
4. Controleer dat de akkoordtonen als één gemixte chord buffer hoorbaar zijn.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 10 --note-duration 0.25 --voice-mode gated --dedupe-window 0.03 --chord-window 0.02 --debuglevel verbose
```

Verwachte CLI-indicaties:

```text
Gated MVP note: note_on plays an audible fallback buffer and note_off reports duration; polyphonic chord batches are mixed
Streaming MIDI audio trigger settings: ... chord_window=0.02s ...
Streamed sequence events: C4@..., E4@..., G4@...
```

Acceptatie:

- Drie gelijktijdige note-on events worden als triad gemixt.
- Note-on events buiten `--chord-window` blijven aparte buffers.
- `--dedupe-window` onderdrukt duplicate echo-events zonder verschillende chord tones te verwijderen.
- `--voice-mode fixed` en `--voice-mode gated` blijven beide werken.
- Eventuele kleine latency en pulse-achtig nootgedrag zijn toegestaan binnen US-034; echte sustained playback blijft US-035.

Product Owner acceptatie op 2026-07-11:

- Test met `--chord-window 0.08` speelde hoorbaar akkoordachtige groepen.
- CLI toonde `Streamed 17 MIDI-triggered note events` en `suppressed 0 duplicate MIDI messages`.
- US-034 status: `Done`.

## Traceability

- ChatID: CHATOD-20260709-D1PY-MVP-001 / US-034
- Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-034 Polyphonic Voice Mixer En Triads
- Version: 0.1.0
