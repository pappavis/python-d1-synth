# US-029 Logic/DAW Virtual MIDI Naar Audio Trigger

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-029-VIRTUAL-MIDI-AUDIO-001  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Epic: EPIC-007 Future MIDI En DAW Integratie  
User Story: US-029 Logic/DAW Virtual MIDI Naar Audio Trigger  
Status: Done

## Doel

US-029 combineert de bewezen onderdelen uit US-027 en US-028. De commandline opent zelf een virtual MIDI input port met de naam `python-d1-synth`, Logic Pro 12.3 of een andere DAW routeert note events naar die destination, en de bestaande synth-engine speelt de ontvangen noten hoorbaar af via de gekozen audio-output.

Deze story blijft commandline-only. Het is geen Software Instrument, geen AU, geen VST3, geen Logic Component, geen GUI en geen onbeperkte realtime performance-loop.

## Command

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-virtual --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 2 --timeout 10 --debuglevel light
```

Opties:

- `--port-name`: virtual MIDI destination naam die in Logic/DAW zichtbaar moet worden.
- `--audio-device`: optionele audio-output selectie via dezelfde route als US-011 en US-028.
- `--max-messages`: bounded aantal MIDI note messages voor de test.
- `--timeout`: bounded testduur in seconden.
- `--waveform`, `--sample-rate`, `--channel`: dezelfde synth-render opties als `midi play-live`.

Belangrijk MVP-gedrag: audio wordt in US-029 nog batchgewijs gerenderd nadat `--max-messages` bereikt is of `--timeout` afloopt. Voor de eerste Logic-test is `--max-messages 2 --timeout 10` daarom praktischer dan een langere batch.

Diagnosecommand wanneer Logic de destination wel toont maar er geen geluid komt:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-virtual --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 1 --timeout 10 --debuglevel verbose
```

Speel daarna precies één noot vanuit Logic. Bij ontvangst toont de CLI `Received MIDI messages: note_on:60:velocity=96:channel=1` of vergelijkbare waarden. Als Logic geen MIDI naar Python stuurt, toont de CLI `Received 0 MIDI note messages from virtual MIDI port python-d1-synth; no audio played.`

## Implementatie

- `MidoVirtualMidiInputBackend` opent `mido.open_input(port_name, virtual=True)` en leest bounded note messages.
- `VirtualMidiAudioTriggerSettings` bewaart portnaam, timeout, message-limit, waveform, sample rate, kanaal en audio device.
- `VirtualMidiAudioTriggerResult` rapporteert ontvangen messages, gespeelde events en audio frames.
- `VirtualMidiAudioTrigger` hergebruikt `LiveMidiInputReceiver`, `MidiAudioTrigger`, `SynthEngine` en `SoundDeviceAudioPlayer`.
- `midi play-virtual` gebruikt geen hardcoded MIDI device names. Alleen de default virtual port name `python-d1-synth` is een productnaam/default die via CLI overschrijfbaar is.

## Teststrategie

Automatische tests gebruiken een fake receiver en fake audio player. Daardoor wordt geen echte CoreMIDI/Logic sessie geopend tijdens `pytest`.

Red phase:

- CLI-test faalt zolang `midi play-virtual` niet bestaat.
- Unit-test faalt zolang `VirtualMidiAudioTriggerSettings`, `VirtualMidiAudioTriggerResult`, `MidoVirtualMidiInputBackend` en `VirtualMidiAudioTrigger` ontbreken.
- Traceability-test faalt zolang US-029 metadata ontbreekt.

Green phase:

- Fake Logic/DAW MIDI note events worden naar `NoteSequence` gemapt.
- De bestaande `SynthEngine` rendert een stereo audio buffer.
- De fake audio player ontvangt de gekozen `--audio-device`.
- Docs-test controleert dit document.

## Handmatige Logic Pro Test

US-029-HARDWARE-TEST:

1. Start de commandline:

```bash
cd /Volumes/data1/Yandex.Disk.localized/michiele/Programmering/Python/python_normaal/github_python_normaal/desktop_synth
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-virtual --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 2 --timeout 10 --debuglevel light
```

2. Open Logic Pro 12.3 terwijl de command loopt.
3. Maak een MIDI / External MIDI track.
4. Kies `MIDI Destination: python-d1-synth`.
5. Kies voor de eerste test `MIDI Channel: All` of `1`.
6. Maak een korte MIDI region met 1 of 2 noten, of gebruik Musical Typing om noten naar de External MIDI track te sturen.
7. Start playback of speel de noten terwijl de Python command loopt.
8. Verwacht: hoorbaar geluid via de gekozen audio-output nadat `--max-messages` bereikt is of `--timeout` afloopt, plus CLI output met `Played ... MIDI-triggered note events from virtual MIDI port python-d1-synth.`

Als `python-d1-synth` niet zichtbaar is, herhaal eerst de US-027 zichtbaarheidstest met `midi virtual-port --name python-d1-synth --timeout 60 --debuglevel light`. Dat is dan een virtual-port/DAW zichtbaarheid issue, niet een plugin-issue.

## Impediment US-029-IMPEDIMENT-001

Testresultaat op 2026-07-11 00:20:

- Logic Pro toont `python-d1-synth` als External MIDI destination.
- De test-track was ingesteld op `MIDI Destination: python-d1-synth`.
- De eerste poging gebruikte `MIDI Channel: All`.
- Er was geen hoorbaar geluid tijdens de lange test.
- `Ctrl-C` stopte de command niet duidelijk genoeg.

Oplossing in deze impediment-fix:

- README en dit document specificeren expliciet `MIDI Destination: python-d1-synth` en `MIDI Channel: All` of `1`.
- De aanbevolen testcommand gebruikt `--max-messages 2 --timeout 10`.
- De CLI legt uit dat audio in deze MVP pas speelt na max-messages of timeout.
- De CLI handelt `Ctrl-C` af met `Virtual MIDI audio trigger interrupted by user.` en exit code `130`.

## Impediment US-029-IMPEDIMENT-002

Eerste testresultaat:

- Logic Pro toont `python-d1-synth` als External MIDI destination.
- Er is een MIDI region opgenomen via `SMK 37 Pro`.
- De External Instrument track gebruikt `MIDI Destination: python-d1-synth` en `MIDI Channel: All`.
- Bij afspelen kwam geen hoorbaar geluid uit de Python synth.

Diagnosewijziging:

- `VirtualMidiAudioTriggerResult` bevat nu de ontvangen `MidiMessage` items.
- `midi play-virtual --debuglevel verbose` toont ontvangen note messages met type, note number, velocity en channel.
- Bij timeout zonder MIDI wordt expliciet `Received 0 MIDI note messages from virtual MIDI port python-d1-synth; no audio played.` getoond.
- De aanbevolen diagnose gebruikt `--max-messages 1 --timeout 10 --debuglevel verbose`, zodat één note-on genoeg is om de Logic-to-Python route te bewijzen.

Tweede testresultaat:

CHATOD-20260709-D1PY-MVP-001 / US-029-IMPEDIMENT-002-PUBLISHED

```text
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-virtual --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 1 --timeout 10 --debuglevel verbose
Selected audio device from cli: Scarlett 8i6 USB
Opening virtual MIDI input port: python-d1-synth
Keep this command running while Logic Pro or another DAW sends notes to this MIDI destination.
MVP note: audio is rendered after --max-messages is reached or --timeout expires; use --max-messages 2 --timeout 10 for a quick Logic test.
Virtual MIDI audio trigger settings: port=python-d1-synth, max_messages=1, timeout=10s, waveform=sine, sample_rate=44100 Hz, channel=stereo
Played 1 MIDI-triggered note events from virtual MIDI port python-d1-synth.
Received MIDI messages: note_on:60:velocity=50:channel=1
Audio buffer: 44100 frames, 44100 Hz
```

Beoordeling: geslaagd. De MIDI region track in Logic Pro stuurde note events naar de virtual MIDI port, Python ontving `note_on:60:velocity=50:channel=1`, en er werd hoorbaar geluid afgespeeld via `Scarlett 8i6 USB`.

## Acceptatiecriteria

- `midi play-virtual` opent een virtual MIDI input port en ontvangt bounded MIDI note messages.
- Logic Pro 12.3 of een andere DAW kan tijdens de command naar `python-d1-synth` routen.
- Ontvangen note events worden via de bestaande US-024/US-026 mapping naar `NoteSequence` vertaald.
- De bestaande US-028 audio-trigger route maakt hoorbaar audio via `SoundDeviceAudioPlayer`.
- CLI ondersteunt `--port-name`, `--audio-device`, `--max-messages`, `--timeout`, `--waveform`, `--sample-rate`, `--channel` en `--debuglevel`.
- CLI geeft bij `Ctrl-C` een duidelijke onderbrekingsmelding en exit code `130`.
- CLI toont bij `--debuglevel verbose` ontvangen MIDI note messages of expliciet nul ontvangen MIDI messages.
- Unit tests gebruiken fake receiver en fake audio player.
- Geen GUI, geen plugin, geen AU/VST3, geen Logic Component en geen onbeperkte realtime performance-loop.
- Er zijn geen hardcoded MIDI hardware device names toegevoegd.

## Status

US-029 status: `Done`. Automatische tests zijn groen en de handmatige Logic Pro test bevestigt hoorbaar geluid vanuit een MIDI region naar `python-d1-synth`.
