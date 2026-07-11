# US-031 Live/Streaming MIDI Playback Loop

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-031-LIVE-STREAMING-001  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Epic: EPIC-007 Future MIDI En DAW Integratie  
Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog  
User Story: US-031 Live/Streaming MIDI Playback Loop  
Status: Done

## Doel

US-031 verlaagt de hoorbare vertraging uit US-030. In plaats van eerst een volledige MIDI batch te verzamelen en daarna een sequence te renderen, speelt `midi play-stream` elke ontvangen `note_on` direct af als een korte fixed-duration audio buffer.

Dit is een MVP streaming-loop, geen professionele low-latency audio engine. `note_off`, sustain, overlap/polyfonie, pitch bend, modulation, GUI, AU, VST3 en Logic Component blijven buiten US-031.

## Testcommand Voor Logic Pro 12.3

```bash
cd /Volumes/data1/Yandex.Disk.localized/michiele/Programmering/Python/python_normaal/github_python_normaal/desktop_synth
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 30 --note-duration 0.25 --debuglevel verbose
```

Logic/DAW setup:

- Maak een `MIDI > External MIDI` track.
- Kies `MIDI Destination: python-d1-synth`.
- Kies `MIDI Channel: All` of `1`.
- Speel losse noten of een korte MIDI region.
- Vergelijk de hoorbare vertraging met de US-030 batchroute.

Verwacht CLI-gedrag:

- `Opening streaming virtual MIDI input port: python-d1-synth`
- `Near-realtime MVP note: note_on events are played as short fixed-duration audio buffers`
- `Received MIDI messages: ...`
- `Streamed sequence events: C4@..., D4@...`
- `Streamed 2 MIDI-triggered note events from virtual MIDI port python-d1-synth.`

## Technische Implementatie

- `MidoStreamingVirtualMidiInputBackend` opent een virtual MIDI input port met `mido.open_input(port_name, virtual=True)` en yieldt note messages tijdens de receive-loop.
- `StreamingMidiAudioTrigger` rendert per ontvangen `note_on` een korte `NoteEvent` en speelt direct een audio buffer af.
- `StreamingMidiAudioTriggerResult` bewaart received messages, played events en totaal aantal audio frames.
- `midi play-stream` gebruikt dezelfde audio-device, waveform, sample-rate en channel opties als de batchroutes.

## Red Phase

- Unit test faalt zonder streaming backend contract.
- Unit test faalt als twee `note_on` messages niet twee audio-player calls maken.
- CLI test faalt zolang `midi play-stream` ontbreekt.
- Traceability-test faalt zonder US-031 metadata in code docstrings.

## Green Phase

- `tests/test_midi.py` dekt streaming playback per `note_on`, no-audio bij alleen `note_off`, en settings-validatie.
- `tests/test_cli.py` dekt `midi play-stream`, verbose diagnostics en `KeyboardInterrupt`.
- `tests/test_traceability.py` dekt ChatOD, backlog, epic, user story en versie.
- `tests/test_docs.py` dekt dit document.

## Acceptatiecriteria

- Logic/DAW kan `note_on` events naar `python-d1-synth` sturen terwijl `midi play-stream` draait.
- De synth speelt per `note_on` een korte hoorbare noot zonder te wachten op `--max-messages` of `--timeout`.
- De latency is merkbaar lager dan US-030 batch playback.
- Verbose output toont ontvangen MIDI messages en gestreamde sequence events.
- Geen hardcoded MIDI hardware device names.

## Status

US-031 staat op `Done`. De Product Owner bevestigde dat Logic Pro streaming playback hoorbaar werkt.

Handmatige test op 2026-07-11:

```text
Streamed 18 MIDI-triggered note events from virtual MIDI port python-d1-synth.
Received MIDI messages: note_on:53:velocity=54:channel=1, note_on:53:velocity=54:channel=1, note_off:53:velocity=64:channel=1, note_off:53:velocity=64:channel=1, note_on:60:velocity=91:channel=1, note_on:60:velocity=91:channel=1
Streamed sequence events: F3@1.153s, F3@1.153s, C4@2.099s, C4@2.099s, A3@3.098s, A3@3.098s
Total streamed audio frames: 198450, sample_rate=44100 Hz
```

Product Owner opmerking: realtime noten spelen hoorbaar af. De MIDI-route levert sommige events dubbel aan, waardoor een noot twee keer hoorbaar kan zijn. Dit hoort bij US-032 Duplicate MIDI Event Guard, niet bij US-031.
