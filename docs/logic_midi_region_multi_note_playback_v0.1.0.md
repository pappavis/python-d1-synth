# US-030 Logic MIDI Region Multi-Note Playback

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-030-LOGIC-MULTI-NOTE-001  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Epic: EPIC-007 Future MIDI En DAW Integratie  
Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog  
User Story: US-030 Logic MIDI Region Multi-Note Playback  
Status: In Review

## Doel

US-030 breidt de bewezen US-029 route uit van "een eerste hoorbare noot uit Logic" naar een korte MIDI region met meerdere noten. De commandline opent nog steeds zelf de virtual MIDI input port `python-d1-synth`, ontvangt bounded MIDI messages, mapt die naar `NoteEvent`s en rendert daarna een hoorbare `NoteSequence`.

Dit is bewust batchgewijs. Audio speelt nadat `--max-messages` bereikt is of `--timeout` afloopt. Continue realtime streaming, pitch bend, modulation, GUI, AU, VST3 en Logic Component blijven buiten US-030.

## Testcommand Voor Logic Pro 12.3

```bash
cd /Volumes/data1/Yandex.Disk.localized/michiele/Programmering/Python/python_normaal/github_python_normaal/desktop_synth
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-virtual --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 16 --timeout 10 --debuglevel verbose
```

Logic/DAW setup:

- Maak een `MIDI > External MIDI` track.
- Kies `MIDI Destination: python-d1-synth`.
- Kies `MIDI Channel: All` of `1`.
- Maak een korte MIDI region met meerdere noten, bijvoorbeeld C4, D4, E4.
- Speel de region af terwijl de Python command draait.

Verwacht CLI-gedrag:

- `Opening virtual MIDI input port: python-d1-synth`
- `Received MIDI messages: ...`
- `Rendered sequence events: C4@..., D4@..., E4@...`
- `Played 3 MIDI-triggered note events from virtual MIDI port python-d1-synth.`

## Technische Implementatie

- `MidiMessageNormalizer` accepteert een receive-loop fallback time voor backends die raw MIDI message time als `0.0` rapporteren.
- `MidoMidiInputBackend` en `MidoVirtualMidiInputBackend` gebruiken monotonic elapsed time tijdens de bounded receive-loop.
- `VirtualMidiAudioTriggerResult` bewaart naast received messages ook `played_events`, zodat CLI en tests precies tonen welke `NoteEvent`s gerenderd zijn.
- `VirtualMidiAudioTrigger` rendert de volledige ontvangen `NoteSequence` in plaats van alleen een eerste noot te valideren.
- `SynthCli` toont bij verbose mode zowel ruwe MIDI note messages als gerenderde sequence events.

## Red Phase

- Multi-note MIDI mapping test faalt zonder meerdere geordende `NoteEvent`s.
- Fallback-time test faalt als raw backend time `0.0` blijft.
- Virtual trigger test faalt als maar een noot gerenderd wordt.
- CLI verbose test faalt zonder multi-note sequence output.
- Traceability-test faalt zonder US-030 metadata in code docstrings.

## Green Phase

- `tests/test_midi.py` dekt meerdere Logic-style note-on/off paren, fallback timing en multi-note virtual audio trigger.
- `tests/test_cli.py` dekt verbose multi-note output voor `midi play-virtual`.
- `tests/test_traceability.py` dekt ChatOD, backlog, epic, user story en versie.
- `tests/test_docs.py` dekt dit document.

## Acceptatiecriteria

- Logic/DAW kan meerdere MIDI notes naar `python-d1-synth` sturen in dezelfde bounded run.
- Python ontvangt meerdere MIDI note messages.
- De mapper maakt meerdere `NoteEvent`s met starttijden.
- De synth rendert hoorbare audio voor de volledige batch.
- Verbose output maakt diagnose eenvoudig als Logic wel een destination toont maar geen events stuurt.
- geen hardcoded MIDI hardware device names.

## Status

US-030 staat op `In Review`. De Product Owner moet nog bevestigen dat een Logic Pro MIDI region met meerdere noten hoorbaar als batch afspeelt.
