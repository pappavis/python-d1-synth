# python-d1-synth

ChatOD: CHATOD-20260709-D1PY-MVP-001 / SKELETON-001

`python-d1-synth` is een commandline-first Python monosynth MVP, geinspireerd door klassieke subtractive monosynth workflows. Sprint 1 richt zich op hoorbare audio, WAV-rendering, note parsing, testbare architectuur en later uitbreidbare MIDI/DAW-integratie.

## Development Environment

Target:

- macOS op Mac Mini M4.
- Python 3.11.
- VS Code.
- Virtual environment opgegeven door klant: `/Users/michiele/venv`.
- Gedetecteerde uitvoerbare interpreter uit je `.zshrc`: `/Volumes/data1/michiele/venv/venv3.12/bin/python`.

Let op: in je `.zshrc` activeer je `/Volumes/data1/michiele/venv/venv3.12/bin/activate`. De werkende Python interpreter staat daardoor op `/Volumes/data1/michiele/venv/venv3.12/bin/python`.

## Install

```bash
cd /Volumes/data1/Yandex.Disk.localized/michiele/Programmering/Python/python_normaal/github_python_normaal/desktop_synth
/Volumes/data1/michiele/venv/venv3.12/bin/python -m pip install -e ".[dev,midi]"
```

Wanneer jouw lokale Python 3.11 venv op een ander subpad staat, vervang dan `/Volumes/data1/michiele/venv/venv3.12/bin/python` door het juiste pad.

## Run CLI

Render een WAV-bestand:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth render examples/patch.yaml --output outputs/demo.wav --debuglevel light
```

Speel een noot:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --note C3 --duration 1.0 --channel stereo --debuglevel light
```

Speel een noot via je Scarlett 8i6 USB:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --note C3 --duration 1.0 --channel stereo --audio-device "Scarlett 8i6 USB" --debuglevel verbose
```

Speel een square waveform:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --note C3 --duration 1.0 --waveform square --channel stereo --debuglevel verbose
```

Speel een saw waveform:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --note C3 --duration 1.0 --waveform saw --channel stereo --debuglevel verbose
```

Test kanaalroutering via je Scarlett 8i6 USB:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --note C3 --duration 1.0 --channel stereo --audio-device "Scarlett 8i6 USB" --debuglevel verbose
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --note C3 --duration 1.0 --channel left --audio-device "Scarlett 8i6 USB" --debuglevel verbose
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --note C3 --duration 1.0 --channel right --audio-device "Scarlett 8i6 USB" --debuglevel verbose
```

Speel een testsequence:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --testsequence "ACGD" --duration 0.25 --debuglevel light
```

Speel dezelfde testsequence via je Scarlett 8i6 USB:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --testsequence "ACGD" --duration 0.25 --channel stereo --audio-device "Scarlett 8i6 USB" --debuglevel verbose
```

Scan audio devices:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth audio list-devices --debuglevel light
```

Scan MIDI devices:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi list-devices --unsafe-rtmidi-scan --debuglevel light
```

Selecteer een MIDI input uit de scan via naam of identifier:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi list-devices --unsafe-rtmidi-scan --midi-device "deel van device naam" --debuglevel light
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi list-devices --unsafe-rtmidi-scan --midi-device-id "input:0" --debuglevel light
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi list-devices --unsafe-rtmidi-scan --config examples/patch.yaml --debuglevel light
```

Luister bounded naar een gekozen MIDI input zonder audio-trigger:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi listen --unsafe-rtmidi-scan --midi-device "deel van input device naam" --max-messages 10 --timeout 5 --debuglevel light
```

Speel ontvangen MIDI note events bounded af via de synth-engine:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-live --unsafe-rtmidi-scan --midi-device "deel van input device naam" --audio-device "Scarlett 8i6 USB" --max-messages 10 --timeout 10 --debuglevel light
```

Diagnoseer virtual MIDI input voorbereiding:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi diagnose-virtual-input
```

Open een bounded virtual MIDI port voor Logic/DAW zichtbaarheid:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi virtual-port --name python-d1-synth --timeout 60 --debuglevel light
```

Laat dit command draaien terwijl je in Logic Pro 12.3 controleert of `python-d1-synth` als MIDI destination verschijnt.

Open een virtual MIDI port en speel Logic/DAW note events hoorbaar af:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-virtual --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 2 --timeout 10 --debuglevel light
```

Laat dit command draaien en configureer Logic Pro 12.3 als volgt:

- Maak een `MIDI > External MIDI` track.
- Kies `MIDI Destination: python-d1-synth`.
- Kies voor de eerste test `MIDI Channel: All` of `1`.
- Zet een korte MIDI region met 1 of 2 noten op de track, of gebruik Musical Typing.
- Start playback of speel noten terwijl de Python command loopt.

Deze MVP-route rendert audio nadat `--max-messages` bereikt is of `--timeout` afloopt. Gebruik daarom voor de eerste test `--max-messages 2 --timeout 10`. Stoppen met `Ctrl-C` hoort netjes te melden dat de virtual MIDI audio trigger door de gebruiker is onderbroken. Dit is nog geen Software Instrument, AU, VST3 of Logic Component.

Als Logic `python-d1-synth` wel toont maar je geen geluid hoort, test dan eerst of Python MIDI ontvangt:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-virtual --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 1 --timeout 10 --debuglevel verbose
```

Speel daarna exact één noot vanuit Logic. Bij succes zie je iets zoals `Received MIDI messages: note_on:60:velocity=96:channel=1`. Bij geen MIDI-route zie je `Received 0 MIDI note messages from virtual MIDI port python-d1-synth; no audio played.`

Diagnoseer generieke USB MIDI input voorbereiding:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi diagnose-usb-input --unsafe-rtmidi-scan --midi-device "SMK-37"
```

MIDI testprocedure: eerst devices lijsten, daarna een device kiezen of als default noteren. Leg altijd vast of de test op `KodeklopperM4` of `MuziekM4` draait.

US-022 blocker hardwaretest:

```bash
PYTHON_D1_RUN_HARDWARE_MIDI=1 PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m pytest tests/test_hardware_midi.py -s
```

Deze test gaat ervan uit dat er MIDI devices aangesloten zijn. Als Logic Pro devices toont maar Python niets vindt, meldt de test dit als blocker.

Selecteer later een MIDI device:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --midi-device "Arturia KeyLab Mk3" --debuglevel light
```

## Debuglevel

`--debuglevel` ondersteunt drie niveaus:

- `none`: geen statusregels, alleen noodzakelijke fouten.
- `light`: hoofdacties zoals `Playing note C3`.
- `verbose`: hoofdacties plus technische details zoals waveform, duration, sample rate, channel en audio-buffer.

Voorbeeld:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth play --note C3 --duration 1.0 --debuglevel verbose
```

## Tests

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m pytest
```

De testcode gebruikt `pytest` en volgt de afgesproken red/green werkwijze per user story.

## VS Code

Open deze map als workspace:

```bash
code /Volumes/data1/Yandex.Disk.localized/michiele/Programmering/Python/python_normaal/github_python_normaal/desktop_synth
```

De launch-config bevat:

- `python-d1-synth: play C3`
- `python-d1-synth: play C3 Scarlett`
- `python-d1-synth: play C3 Scarlett left`
- `python-d1-synth: play C3 Scarlett right`
- `python-d1-synth: play ACGD Scarlett`
- `python-d1-synth: render patch`
- `python-d1-synth: list audio devices`
- `python-d1-synth: list MIDI devices`

Als VS Code jouw venv niet automatisch kiest, zet de interpreter handmatig naar jouw daadwerkelijke venv-python.

## Code Traceability

Nieuwe code die vanaf US-013 wordt toegevoegd of geraakt, krijgt traceerbare metadata in docstrings:

- Chatlog ID, bijvoorbeeld `CHATOD-20260709-D1PY-MVP-001`.
- Backlognaam, bijvoorbeeld `Sprint 1 Kanban Backlog`.
- Epicnummer en epicnaam, bijvoorbeeld `EPIC-002 Muzikale Basisdata`, `EPIC-003 Oscillator En Audio Rendering`, `EPIC-004 Realtime CLI Playback` of `EPIC-005 Configuratie En CLI`.
- User story nummer en titel, bijvoorbeeld `US-006 NoteEvent En NoteSequence Model`, `US-008 Saw Oscillator`, `US-009 Square Oscillator`, `US-013 Channel Selection` of `US-016 Debuglevel`.
- Projectversie, bijvoorbeeld `0.1.0`.

## MIDI Troubleshooting

MIDI leerpad:

- [MIDI Leerpad En Terminologie](docs/midi_learning_path_v0.1.0.md)
- [Virtual MIDI Input Voor DAW](docs/virtual_midi_input_v0.1.0.md)
- [External MIDI Workflow In Logic](docs/logic_external_midi_workflow_v0.1.0.md)
- [USB MIDI Hardware Input](docs/usb_midi_hardware_input_v0.1.0.md)
- [Studio MIDI Routing Integratietest](docs/studio_midi_routing_integration_v0.1.0.md)
- [MIDI Naar NoteEvent Mapping](docs/midi_to_note_event_mapping_v0.1.0.md)
- [MIDI Device Discovery En Default Selection](docs/midi_device_discovery_default_selection_v0.1.0.md)
- [Live MIDI Input Receive Loop](docs/live_midi_input_receive_loop_v0.1.0.md)
- [Virtual MIDI Port Voor Logic/DAW](docs/virtual_midi_port_logic_daw_v0.1.0.md)
- [External MIDI Audio Trigger Integratie](docs/external_midi_audio_trigger_v0.1.0.md)
- [Logic/DAW Virtual MIDI Naar Audio Trigger](docs/virtual_midi_audio_trigger_v0.1.0.md)

Op macOS kan `python-rtmidi`/CoreMIDI hard aborten bij device discovery, bijvoorbeeld met `MidiInCore::initialize: error creating OS-X MIDI client object (-10833)`. De crashrapporten die tijdens US-011 zijn bekeken wijzen naar `_rtmidi` en CoreMIDI. Dat is de MIDI-scanroute, niet de audio-outputroute naar bijvoorbeeld `Scarlett 8i6 USB`.

De skeleton voert MIDI device scanning daarom in een apart subprocess uit. Als RtMidi crasht, blijft de hoofd-CLI overeind en meldt `midi list-devices` dat er geen devices gevonden zijn of dat de backend niet bruikbaar is.

US-022 is afgerond: na herstel van de MIDI Python packages toont `midi list-devices --unsafe-rtmidi-scan --debuglevel light` in een gewone Terminal op `KodeklopperM4` echte MIDI input- en outputdevices, waaronder `Scarlett 8i6 USB`, `SMK-37 Pro_BLE Bluetooth` en `SN76489 Synth Pappavis CircuitPython usb_midi.ports[0]`.

Tijdens US-022 is een package-conflict opgelost: het verkeerde pakket `rtmidi 2.5.0` stond naast `python-rtmidi 1.5.8` en overschreef de module die Mido verwacht. Na verwijderen van `rtmidi` en herinstalleren van `python-rtmidi==1.5.8` is `rtmidi.API_UNSPECIFIED` weer beschikbaar. In de Codex-run context kan CoreMIDI scanning nog crashen met `MidiInCore::initialize: error creating OS-X MIDI client object (-10833)`, daarom blijft de scan standaard veilig uit en gebruiken we `--unsafe-rtmidi-scan` alleen voor bewuste hardwarediagnose.

US-023 legt de studio MIDI routing testmatrix vast. Device-namen uit `KodeklopperM4`, `MuziekM4`, toekomstig Windows `Spelen01` of Raspberry Pi 2 zijn runtime snapshots en mogen niet als constants in applicatiecode worden vastgelegd.

US-024 is afgerond: `MidiToNoteEventMapper` vertaalt device-onafhankelijke `MidiMessage` note-on/off berichten naar `NoteEvent` en `NoteSequence`. De mapper behandelt `note_on` met velocity `0` als note-off, houdt channels gescheiden en gebruikt een default duration wanneer een note-off ontbreekt.

US-025 is afgerond: `midi list-devices` kan naast scannen ook een MIDI input selecteren via `--midi-device`, `--midi-device-id` of `midi.default_input_device` uit `--config`. CLI wint van YAML en runtime device-namen blijven scanresultaten, geen hardcoded constants.

US-026 is afgerond: `midi listen` kan bounded note messages ontvangen van een gekozen MIDI input, normaliseren naar `MidiMessage`, en mappen naar `NoteSequence`. Dit is nog geen Logic virtual device en nog geen realtime audio-trigger.

US-027 is afgerond: `midi virtual-port` kan bounded een virtual MIDI input port openen voor Logic/DAW zichtbaarheid. De klanttest in Logic Pro 12.3 bevestigde dat `python-d1-synth` beschikbaar is als External MIDI destination. Niet zichtbaar als Software Instrument / virtual instrument is verwacht; AU/VST3/Logic Component hoort bij latere plugin-packaging stories. Realtime audio-triggering blijft US-028.

US-028 is afgerond: `midi play-live` koppelt bounded ontvangen MIDI note events aan de bestaande synth-engine en audio-output. De klanttest op `KodeklopperM4` bevestigde hoorbaar stereo geluid met `SMK-37 Pro_BLE Bluetooth` naar `Scarlett 8i6 USB`.

US-029 is afgerond: `midi play-virtual` opent zelf een virtual MIDI input port en koppelt ontvangen Logic/DAW note events aan dezelfde synth-engine/audio-output route. De Logic Pro test bevestigde hoorbaar geluid vanuit een MIDI region naar `python-d1-synth`, met `Received MIDI messages: note_on:60:velocity=50:channel=1`. Dit is commandline-only en blijft buiten GUI, AU/VST3, Logic Component en plugin packaging.

US-030 is afgerond: `midi play-virtual` ondersteunt nu een korte Logic/DAW MIDI region met meerdere noten in dezelfde batch. Gebruik voor deze test een hogere `--max-messages` waarde, bijvoorbeeld 16, zodat meerdere note-on/note-off paren binnenkomen voordat audio wordt gerenderd:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-virtual --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 16 --timeout 10 --debuglevel verbose
```

Bevestigd gedrag: Logic stuurde meerdere MIDI events naar `python-d1-synth`, verbose output toonde `Received MIDI messages` en `Rendered sequence events: C4@0.945s, F4@1.062s, F4@1.560s, C4@1.960s, F4@2.200s`, en de batch speelde hoorbaar af. Dit is nog steeds batch-rendering na `--max-messages` of `--timeout`; de waargenomen vertraging van ongeveer 2 seconden is verwacht binnen US-030. Continue realtime streaming, pitch bend en modulation volgen in latere stories.

US-031 is afgerond: `midi play-stream` opent een virtual MIDI input port en speelt `note_on` events direct als korte fixed-duration buffers. Dit verlaagt de US-030 batchvertraging merkbaar:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 30 --note-duration 0.25 --debuglevel verbose
```

Bevestigd gedrag: Logic stuurde 32 MIDI messages, `play-stream` speelde 18 hoorbare note events en de realtime playback was geslaagd. De test toonde ook dubbele note events vanuit de MIDI-route; dat wordt in US-032 opgelost. `note_off`, sustain, overlap/polyfonie, pitch bend en modulation worden nog niet muzikaal toegepast; die volgen in latere stories.

US-032 is afgerond: `midi play-stream` onderdrukt identieke duplicate MIDI messages binnen een korte dedupe-window, zodat Logic/CoreMIDI echo-paren niet dubbel hoorbaar spelen. Verschillende noten op dezelfde timestamp blijven behouden, zodat latere polyfonie/triads niet door de duplicate guard worden geblokkeerd.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 30 --note-duration 0.25 --dedupe-window 0.03 --debuglevel verbose
```

Controleer in verbose output:

- `dedupe_window=0.03s`
- `suppressed ... duplicate MIDI messages`
- `Suppressed duplicate MIDI messages: ...`
- De `Streamed sequence events` bevat niet meer elk identiek Logic echo-event dubbel.

Bevestigd gedrag: Logic en live note playback waren hoorbaar. De US-032 test speelde 6 MIDI-triggered note events en onderdrukte 23 duplicate MIDI messages. Een kleine resterende latency is bekend en hoort bij latere stories rond note-off gated voice duration, polyfonie en low-latency audio.

US-033 is afgerond: `midi play-stream` ondersteunt nu optioneel `--voice-mode gated`. In deze mode speelt `note_on` direct een hoorbare fallback-buffer en rapporteert `note_off` de gemeten nootduur. Default blijft `--voice-mode fixed`, zodat US-031/US-032 gedrag niet verandert.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 30 --note-duration 0.25 --voice-mode gated --dedupe-window 0.03 --debuglevel verbose
```

Controleer in verbose output:

- `voice_mode=gated`
- `Streamed note durations: ...`
- Korte en lange Logic-noten krijgen verschillende durations.
- Ctrl-C geeft `Streaming MIDI audio trigger interrupted by user.`

Bevestigd gedrag: Product Owner hoorde geluid via Logic/MIDI keyboard. Bij een 2 seconden vastgehouden C3 speelde US-033 bewust nog een kort pulse-nootje, terwijl verbose output de nootduur al rapporteerde. Echte held/sustained audio blijft US-035.

US-034 is afgerond: `midi play-stream` kan note-on events die in dezelfde streaming poll-batch binnenkomen als polyphonic chord buffer mixen. Dit maakt triads/akkoorden hoorbaar zonder de US-033 scope naar sustained voices, pitch bend of modulation uit te breiden.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 10 --note-duration 0.25 --voice-mode gated --dedupe-window 0.03 --chord-window 0.02 --debuglevel verbose
```

Controleer in verbose output:

- `chord_window=0.02s`
- `polyphonic chord batches are mixed`
- Triads zoals C-E-G klinken als één akkoordbuffer in plaats van losse na elkaar gespeelde noten.

Bevestigd gedrag: Product Owner hoorde akkoordachtige groepen met `--chord-window 0.08`; verschillende chord tones bleven behouden en er waren geen duplicate suppressions nodig.

US-035 is afgerond: `midi play-stream` ondersteunt nu `--voice-mode sustained`. In deze mode start `note_on` een actieve streaming voice en stopt `note_off` die voice, zodat een langer vastgehouden toets niet meer alleen als kort pulse-nootje speelt.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 30 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --debuglevel verbose
```

Controleer in verbose output:

- `voice_mode=sustained`
- `Sustained MVP note: note_on starts a streaming voice and note_off stops it`
- Een 2 seconden vastgehouden C3 klinkt ongeveer 2 seconden door.

Bevestigd gedrag: Product Owner testte `--voice-mode sustained`; noten bleven hoorbaar tot note-off en `Total streamed audio frames: 575172` bevestigde streaming audio.

US-036 is afgerond: sustained playback verwerkt MIDI pitch bend messages. Pitch bend wordt standaard per MIDI channel gemapt naar actieve sustained voices. Default bereik is `--pitch-bend-range 2`, dus volledige pitch bend is ongeveer twee semitones omhoog of omlaag.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 30 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --debuglevel verbose
```

Als een controller of DAW note events op een ander MIDI channel stuurt dan pitch bend events, zoals een SMK37/Logic route met note-on op channel 1 en pitch bend op channel 4, gebruik dan de expliciete MVP testmode:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 30 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --debuglevel verbose
```

Controleer in verbose output:

- `voice_mode=sustained`
- `pitch_bend_range=2st`
- `pitch_bend_channel_mode=omni` wanneer cross-channel pitch bend nodig is.
- `Received MIDI messages` bevat `pitch_bend:<waarde>:channel=<n>`.

Bevestigd gedrag: Product Owner hoorde sustained playback, triads, correcte korte/lange noten en bruikbare langere sessies met `--timeout 600`. De commandline stopt netjes met `Ctrl-C`.

US-037 is afgerond: MIDI CC1 modulation wordt genormaliseerd als `control_change` en in `--voice-mode sustained` als eenvoudige vibrato-depth toegepast op actieve voices. Default vibrato is subtiel: `--modulation-vibrato-depth 0.25` en `--modulation-vibrato-rate 5`.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 10000 --max-control-messages 20000 --timeout 600 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --modulation-vibrato-depth 0.25 --modulation-vibrato-rate 5 --debuglevel light
```

Controleer in verbose output:

- `modulation_vibrato_depth=0.25st`
- `modulation_vibrato_rate=5Hz`
- `Received MIDI messages` bevat `control_change:1:<waarde>:channel=<n>` wanneer CC1 binnenkomt.

US-037 interrupt-fix: bij `Ctrl-C` gebruikt sustained streaming nu een immediate audio-stream abort tijdens cleanup, zodat PortAudio/CoreAudio niet eerst langdurig op een gewone `stop()` hoeft te wachten.

Bevestigd gedrag: Product Owner hoorde pitch bend en CC1 modulation hoorbaar werken; de US-037 interrupt-fix is getest en akkoord.

US-038 is afgerond: voor gewoon spelen zonder kunstmatige sessielimiet kan `midi play-stream` nu in performance mode draaien met `--until-interrupt`. In die mode blijven de bestaande `--max-messages` en `--timeout` argumenten geldig voor parser/traceability, maar de runtime gebruikt praktische lange backend-limieten en stopt primair via `Ctrl-C`.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 10000 --max-control-messages 20000 --timeout 600 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --modulation-vibrato-depth 0.25 --modulation-vibrato-rate 5 --until-interrupt --debuglevel light
```

Stoppen:

- Druk `Ctrl-C` in de terminal waar `play-stream` draait.
- Verwachte melding: `Streaming MIDI audio trigger interrupted by user.`

Bevestigd gedrag: Product Owner testte US-038 als geslaagd.

US-039 is afgerond: `midi play-stream --voice-mode sustained` verwerkt nu MIDI CC64 sustain pedal. CC64 waarden `64..127` houden released voices vast; CC64 waarden `0..63` laten de vastgehouden voices los.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 10000 --max-control-messages 20000 --timeout 600 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --modulation-vibrato-depth 0.25 --modulation-vibrato-rate 5 --until-interrupt --debuglevel verbose
```

Controleer in verbose output:

- `control_change:64:127:channel=<n>` bij pedal down
- `control_change:64:0:channel=<n>` bij pedal up
- Losgelaten toetsen blijven hoorbaar zolang CC64 down is.

Bevestigd gedrag: Product Owner heeft geen fysieke sustain pedal en accepteerde US-039 op basis van aanname plus groene automatische CC64-tests.

US-040 is afgerond: `midi play-stream --voice-mode sustained` ondersteunt nu een korte release envelope bij note-off, zodat voices niet meer hard worden afgekapt. De default is `--release-time 0.03`; met `--release-time 0` kun je het oude hard-stop gedrag terugzetten om te vergelijken.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 10000 --max-control-messages 20000 --timeout 600 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --modulation-vibrato-depth 0.25 --modulation-vibrato-rate 5 --release-time 0.03 --until-interrupt --debuglevel verbose
```

Vergelijk eventueel met:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 10000 --max-control-messages 20000 --timeout 600 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --modulation-vibrato-depth 0.25 --modulation-vibrato-rate 5 --release-time 0 --until-interrupt --debuglevel light
```

Controleer in verbose output:

- `release_time=0.03s`
- Note releases klinken zachter dan `--release-time 0`.
- `Ctrl-C` stopt de performance-run zonder hang.

Bevestigd gedrag: Product Owner accepteerde US-040 op 2026-07-12.

US-041 is afgerond: `midi play-stream --voice-mode sustained` ondersteunt nu amplitude ADSR parameters. Dit gebruikt dezelfde sustained voice engine als US-035 t/m US-040, maar voegt attack, decay en sustain-level toe bovenop bestaande release-time.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 10000 --max-control-messages 20000 --timeout 600 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --modulation-vibrato-depth 0.25 --modulation-vibrato-rate 5 --attack-time 0.02 --decay-time 0.12 --sustain-level 0.6 --release-time 0.08 --until-interrupt --debuglevel verbose
```

Controleer in verbose output:

- `attack_time=0.02s`
- `decay_time=0.12s`
- `sustain_level=0.6`
- `release_time=0.08s`

Scope: geen filter envelope, velocity-afhankelijke envelope curves, GUI of plugin.

Bevestigd gedrag: Product Owner accepteerde US-041 op 2026-07-13.

US-042 is in review: `midi play-stream` kan performance defaults uit YAML laden via `--config`. Gebruik dit om de lange live performance command korter en herhaalbaar te maken. Expliciete CLI flags blijven winnen van YAML.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --config examples/midi_performance_patch.yaml --audio-device "Scarlett 8i6 USB" --debuglevel verbose
```

Controleer in verbose output:

- `voice_mode=sustained`
- `pitch_bend_channel_mode=omni`
- `attack_time=0.02s`
- `decay_time=0.12s`
- `sustain_level=0.6`
- `release_time=0.08s`
- `Performance mode: running until Ctrl-C`

Het voorbeeldbestand houdt `audio_device: null`, zodat device-namen zoals `Scarlett 8i6 USB` runtime keuzes blijven en geen constants in de repo worden.

Lessons learned en sprint review:

- [Sprint Lessons Learned En Review](docs/sprint_lessons_learned_review_v0.1.0.md)

Vanaf US-011 is native RtMidi/CoreMIDI scanning op macOS standaard uitgeschakeld, omdat macOS alsnog crashrapporten toont wanneer alleen het scan-subprocess abort. De veilige default is:

```bash
PYTHONPATH=src python -m synth midi list-devices --debuglevel light
```

Alleen voor bewuste backenddiagnose:

```bash
PYTHONPATH=src python -m synth midi list-devices --unsafe-rtmidi-scan --debuglevel verbose
```

## Audio Troubleshooting

Je macOS audio-instellingen tonen `Scarlett 8i6 USB` als outputdevice/default. Test eerst vanuit je gewone Terminal, niet vanuit een gesandboxte Codex-run:

```bash
cd /Volumes/data1/Yandex.Disk.localized/michiele/Programmering/Python/python_normaal/github_python_normaal/desktop_synth
source /Volumes/data1/michiele/venv/venv3.12/bin/activate
PYTHONPATH=src python -m synth audio list-devices --debuglevel verbose
PYTHONPATH=src python -m synth play --note C3 --duration 1.0 --channel stereo --audio-device "Scarlett 8i6 USB" --debuglevel verbose
```

Als `audio list-devices` geen devices toont in Codex maar macOS ze wel toont, is dat waarschijnlijk sessie-/permissioncontext. Voer de test dan direct in je eigen Terminal of VS Code terminal uit.

## Sprint 1 Scope

Agile artefacts:

- [Sprint 1 Epic 003 Review](docs/sprint_1_epic_003_review_v0.1.0.md)
- [Sprint 1 Sessie](docs/sprint_1_session_v0.1.0.md)

In scope:

- CLI skeleton.
- Note parsing.
- Testsequence parsing.
- `NoteEvent` en `NoteSequence`.
- Sine/saw/square oscillator basis.
- Stereo/left/right channel routing.
- WAV writer.
- Audio device discovery and `--audio-device` selection.
- Optional realtime playback via `sounddevice`.
- Optional MIDI device discovery via `mido`.
- Pytest test skeleton.

Out of scope voor Sprint 1:

- GUI.
- VST3.
- Logic AU.
- MIDI performance workflow.
- Standalone macOS/Windows packaging.
- CircuitPython/ESP32 fork.
