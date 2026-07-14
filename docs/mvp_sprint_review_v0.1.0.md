# CHATOD-20260709-D1PY-MVP-001 / MVP Sprint Review

- Sprintnummer: MVP Review
- Doc versie: 0.1.0
- Status: Accepted
- Datum: 2026-07-14
- Scope: US-001 t/m US-042

## Executive Summary

De `python-d1-synth` MVP is geslaagd. Het project begon als een commandline-only Python software synth idee en is uitgegroeid tot een werkende, testbare en gedocumenteerde MIDI/DAW performance prototype.

De MVP bewijst dat Logic Pro MIDI kan sturen naar een virtual MIDI destination `python-d1-synth`, waarna de Python synth hoorbaar audio produceert via de geconfigureerde audio-output. De performance route is YAML-driven, zodat een gebruiker met minimale commandline instructies kan starten en alleen overrides gebruikt wanneer nodig.

## MVP Doel

Het doel was niet om al een commerciele plugin of desktop UI te leveren. Het doel was een technisch overtuigend MVP-demo:

- hoorbare audio;
- testbare synth core;
- MIDI/DAW integratie via commandline;
- Logic Pro External MIDI workflow;
- YAML patch en performance config;
- Agile traceability via user stories, acceptatiecriteria, Kanban en docs.

## Geleverde Functionaliteit

- Python package en CLI entrypoint.
- Sine, saw en square oscillator basis.
- Note parsing, `NoteEvent` en `NoteSequence`.
- Stereo, left en right channel routing.
- WAV export.
- Audio device discovery en audio playback via `sounddevice`.
- MIDI terminology learning path.
- MIDI device discovery en default selection.
- Live MIDI receive loop.
- Virtual MIDI destination voor Logic/DAW.
- Logic/DAW MIDI naar hoorbare audio.
- Streaming MIDI playback.
- Duplicate MIDI event guard.
- Note-off duration handling.
- Polyphonic chord batching en triads.
- Sustained note audio engine.
- Pitch bend mapping.
- CC1 modulation mapping.
- Performance mode until interrupt.
- CC64 sustain pedal handling.
- Soft note-off release.
- Amp ADSR parameters.
- YAML performance patch config.

## Acceptatiebewijs

Laatste Product Owner acceptatie:

```text
US-042 test geslaagd: play-stream start via examples/midi_performance_patch.yaml,
Logic stuurt MIDI naar python-d1-synth, en er is hoorbaar geluid via Scarlett 8i6 USB.
```

Dit bevestigt de volledige MVP route:

```text
Logic Pro -> External MIDI -> python-d1-synth virtual MIDI -> Python synth engine -> audio output
```

## Story Sanity Check

`docs/user_stories.md` bevat alle stories van `US-001` tot en met `US-042`. Er ontbreken geen story IDs in de MVP-reeks.

Status op 2026-07-14:

- `US-001` t/m `US-018`: Sprint 0 / Sprint 1 foundation en audio MVP.
- `US-019` t/m `US-042`: Future MIDI/DAW integratie tot en met YAML performance config.
- Alle 42 stories staan op `Done` in de Kanban bron.

## Demo Script

1. Installeer de repo in een lokale virtual environment.
2. Kies audio defaults in `examples/midi_performance_patch.yaml`.
3. Start:

```bash
python -m synth midi play-stream --config examples/midi_performance_patch.yaml
```

4. Open Logic Pro.
5. Maak een External MIDI track.
6. Kies `MIDI Destination: python-d1-synth`.
7. Speel een MIDI region of Musical Typing.
8. Verwacht hoorbare sustained synth audio.

## Scopegrenzen

Bewust niet in de MVP:

- GUI.
- AU/VST3/Logic Component plugin.
- Standalone macOS/Windows packaging.
- Volledige subtractive synth voice met filter.
- Productieklare low-latency audio engine.
- CircuitPython/ESP32 port.

## Kwaliteit En Governance

- Pytest suite: 196 passed, 1 skipped hardware MIDI test.
- Hardware MIDI test is opt-in via `PYTHON_D1_RUN_HARDWARE_MIDI=1`.
- Kanban workbook: `outputs/CHATOD-20260709-D1PY-MVP-001/python_d1_synth_sprint_1_kanban_backlog.xlsx`.
- Traceability: ChatOD, story IDs, docs en code docstrings voor story work.
- README is herschreven voor Logic Pro gebruikers met weinig commandline ervaring.

## Conclusie

De MVP is een professioneel bruikbare basis voor de volgende productbeslissing. De belangrijkste vraag is nu niet meer "kan Python hoorbaar reageren op Logic MIDI?", maar "welke productrichting levert de meeste waarde in de volgende sprint?"

Aanbevolen keuzerichtingen:

- Synth character: filter cutoff/resonance en echte subtractive synth controls.
- Usability: eenvoudige desktop UI of patch manager.
- Delivery: packaged macOS/Windows standalone app.
- Plugin path: AU/VST3 feasibility spike.
- Hardware path: CircuitPython/ESP32 feasibility spike.
