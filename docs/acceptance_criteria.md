# python-d1-synth Acceptance Criteria

ChatOD: CHATOD-20260709-D1PY-MVP-001 / ARTEFACTS-001
Datum: 2026-07-09
Status: Draft for customer review

## Algemene Criteria

- Alle code die later wordt gegenereerd is class based.
- Er worden geen globale variabelen gebruikt.
- De projectstructuur ondersteunt starten via commandline en VS Code debug mode.
- Tests worden geschreven met `pytest`.
- Elke implementatie-story volgt red/green: eerst falende test, daarna minimale implementatie, daarna groene test.
- Sprint 1 blijft commandline-only.
- MIDI, GUI, VST3, Logic AU en standalone packaging blijven buiten Sprint 1.
- Logic Pro 12.3, andere DAWs, USB MIDI en external MIDI worden als future scope gedocumenteerd en mogen de Sprint 1 MVP niet blokkeren.

## US-001: Project Skeleton

- Given een nieuwe checkout van het project, when de ontwikkelaar de setup-instructies volgt, then de package lokaal gestart kan worden.
- Given VS Code, when de debug configuratie wordt gekozen, then een CLI command onder debugger gestart kan worden.
- Given de codebase, then modules logisch gescheiden zijn voor CLI, notes, synth engine, audio output en config.

## US-002: Testframework

- Given het project, when `pytest` wordt uitgevoerd, then de test suite start zonder importfouten.
- Given een nieuwe story, then de bijbehorende test eerst rood kan falen voordat implementatie wordt toegevoegd.

## US-003: VS Code Debug Configuratie

- Given VS Code, when de launch-config wordt gestart, then een voorbeeldcommand zoals `play --note C3` kan debuggen.
- Given commandline argumenten, then deze vanuit de debug configuratie aanpasbaar zijn.

## US-004: Note Parsing

- Given `C3`, when de note parser draait, then een frequentie dicht bij `130.81 Hz` wordt berekend.
- Given `A4`, when de note parser draait, then `440.0 Hz` wordt berekend.
- Given een ongeldige noot, then een duidelijke foutmelding wordt gegeven.

## US-005: Testsequence Parsing

- Given `ACGD`, when de parser draait, then de reeks wordt gelezen als `A3 C4 G3 D4`.
- Given noten met expliciet octaaf, then het opgegeven octaaf wordt gerespecteerd.
- Given een ongeldige reeks, then de CLI een duidelijke foutmelding geeft.

## US-006: NoteEvent En NoteSequence Model

- Given een noot, duur en velocity, when een `NoteEvent` wordt gemaakt, then het object alle waarden valide bevat.
- Given meerdere events, when een `NoteSequence` wordt gemaakt, then de volgorde behouden blijft.
- Given toekomstige MIDI input, then het model voldoende velden heeft voor note, velocity, duration en timing.
- Given US-006 code wordt aangepast, then de betrokken code-docstrings ChatOD, backlog, epicnummer, user story nummer en versie bevatten.

Acceptatie op 2026-07-09:

- Geautomatiseerde tests verifieren `NoteEvent` validatie voor duration, velocity en start time.
- Geautomatiseerde tests verifieren dat `NoteSequence` event-volgorde behoudt, events naar tuple normaliseert en non-`NoteEvent` items weigert.
- Traceability-tests verifieren `CHATOD-20260709-D1PY-MVP-001`, `Sprint 1 Kanban Backlog`, `EPIC-002 Muzikale Basisdata`, `US-006 NoteEvent En NoteSequence Model` en `Version: 0.1.0`.

## US-007: Sine Oscillator

- Given frequentie, duur en sample rate, when de sine oscillator samples genereert, then het aantal samples klopt.
- Given amplitude-limieten, then samples binnen `-1.0` en `1.0` blijven.
- Given een vaste input, then output deterministisch testbaar is.

## US-008: Saw Oscillator

- Given frequentie, duur en sample rate, when de saw oscillator samples genereert, then het aantal samples klopt.
- Given amplitude-limieten, then samples binnen `-1.0` en `1.0` blijven.
- Given saw output, then de samples meerdere ramp-niveaus bevatten en zowel positieve als negatieve waarden bevatten.
- Given US-008 code wordt aangepast, then de betrokken code-docstrings ChatOD, backlog, epicnummer, user story nummer en versie bevatten.

Acceptatie op 2026-07-09:

- Geautomatiseerde tests verifieren saw sample count, amplitude-limieten, positieve/negatieve samples en meerdere ramp-niveaus.
- Traceability-tests verifieren `CHATOD-20260709-D1PY-MVP-001`, `Sprint 1 Kanban Backlog`, `EPIC-003 Oscillator En Audio Rendering`, `US-008 Saw Oscillator` en `Version: 0.1.0`.

## US-009: Square Oscillator

- Given frequentie, duur en sample rate, when de square oscillator samples genereert, then het aantal samples klopt.
- Given amplitude-limieten, then samples binnen `-1.0` en `1.0` blijven.
- Given square output, then samples alleen de twee amplitude-niveaus `-amplitude` en `+amplitude` bevatten.
- Given US-009 code wordt aangepast, then de betrokken code-docstrings ChatOD, backlog, epicnummer, user story nummer en versie bevatten.

Acceptatie op 2026-07-09:

- Geautomatiseerde tests verifieren square sample count, amplitude-limieten en discrete `-0.2`/`+0.2` niveaus.
- Traceability-tests verifieren `CHATOD-20260709-D1PY-MVP-001`, `Sprint 1 Kanban Backlog`, `EPIC-003 Oscillator En Audio Rendering`, `US-009 Square Oscillator` en `Version: 0.1.0`.

## US-010: WAV Export

- Given een patch-config, when `render patch.yaml --output demo.wav` draait, then `demo.wav` wordt aangemaakt.
- Given stereo output, then het WAV-bestand twee kanalen bevat.
- Given sample rate `44100`, then het WAV-bestand die sample rate gebruikt.
- Given US-010 code wordt aangepast, then de betrokken code-docstrings ChatOD, backlog, epicnummer, user story nummer en versie bevatten.

Acceptatie op 2026-07-09:

- CLI render schrijft een stereo WAV op basis van `examples/patch.yaml`.
- Traceability-tests verifieren `CHATOD-20260709-D1PY-MVP-001`, `Sprint 1 Kanban Backlog`, `EPIC-003 Oscillator En Audio Rendering`, `US-010 WAV Export` en `Version: 0.1.0`.

## US-011: Play Single Note

- Given `python -m synth play --note C3`, when de command draait, then realtime audio hoorbaar wordt afgespeeld.
- Given geen duur is meegegeven, then default `1.0` seconde wordt gebruikt.
- Given `--duration 2.5`, then playback ongeveer `2.5` seconden duurt.
- Given `python -m synth audio list-devices`, when de command draait in een gewone macOS Terminal of VS Code terminal, then beschikbare output devices zoals `Scarlett 8i6 USB` zichtbaar kunnen worden.
- Given `--audio-device "Scarlett 8i6 USB"`, when de command draait, then `sounddevice` dit device als output probeert te gebruiken.
- Given audio playback faalt, then de CLI een duidelijke foutmelding toont en adviseert om `audio list-devices` te draaien.

Acceptatie op 2026-07-09:

- `audio list-devices` toont `Scarlett 8i6 USB` als Core Audio outputdevice.
- `play --note C3 --duration 1.0 --channel stereo --audio-device "Scarlett 8i6 USB"` speelde hoorbaar geluid af.

## US-012: Play Testsequence

- Given `python -m synth play --testsequence "ACGD"`, when de command draait, then vier noten achter elkaar hoorbaar zijn.
- Given default mapping, then de reeks `A3 C4 G3 D4` gebruikt.
- Given `--duration 0.25`, then vier noten samen ongeveer `1.0` seconde audio-buffer opleveren op `44100 Hz`.
- Given `--debuglevel verbose`, then de CLI de sequence-events met starttijden toont.
- Given `--audio-device "Scarlett 8i6 USB"`, then dezelfde device-selectie als US-011 gebruikt wordt.

Acceptatie op 2026-07-09:

- Geautomatiseerde tests verifieren `ACGD` als een stereo buffer van `44100` frames bij `44100 Hz`.
- `play --testsequence "ACGD" --duration 0.25 --channel stereo --audio-device "Scarlett 8i6 USB" --debuglevel verbose` speelde hoorbaar een sequence af.
- Verbose output toonde `A3@0.000s, C4@0.250s, G3@0.500s, D4@0.750s`.

## US-013: Channel Selection

- Given `--channel stereo`, then links en rechts audio bevatten.
- Given `--channel left`, then alleen links audio bevat en rechts stil is.
- Given `--channel right`, then alleen rechts audio bevat en links stil is.
- Given US-013 code wordt aangepast, then de betrokken code-docstrings ChatOD, backlog, epicnummer, user story nummer en versie bevatten.

Acceptatie op 2026-07-09:

- Geautomatiseerde tests verifieren stereo, left-only en right-only routing in `ChannelRouter`, `SynthEngine` en CLI.
- `play --note C3 --duration 1.0 --channel stereo --audio-device "Scarlett 8i6 USB"` speelde hoorbaar stereo af.
- `play --note C3 --duration 1.0 --channel left --audio-device "Scarlett 8i6 USB"` speelde hoorbaar links af.
- `play --note C3 --duration 1.0 --channel right --audio-device "Scarlett 8i6 USB"` speelde hoorbaar rechts af.

## US-014: YAML Patch Config

- Given een geldige YAML patch, when deze wordt geladen, then oscillator, duration, sample rate en channel worden gelezen.
- Given een ontbrekende optionele waarde, then een gedocumenteerde default wordt gebruikt.
- Given een ongeldige YAML patch, then de CLI een duidelijke foutmelding geeft.

## US-015: Render Command

- Given `python -m synth render patch.yaml --output demo.wav`, when de command draait, then een WAV-bestand wordt geschreven.
- Given `--debuglevel light`, then de CLI beknopte statusregels toont.

## US-016: Debuglevel

- Given `--debuglevel none`, then alleen noodzakelijke fouten getoond worden.
- Given `--debuglevel light`, then hoofdacties zichtbaar zijn.
- Given `--debuglevel verbose`, then technische details zoals sample rate, waveform, channel en duration zichtbaar zijn.
- Given US-016 code wordt aangepast, then de betrokken code-docstrings ChatOD, backlog, epicnummer, user story nummer en versie bevatten.

Acceptatie op 2026-07-09:

- Geautomatiseerde tests verifieren `DebugReporter` gedrag voor `none`, `light` en `verbose`.
- CLI-tests verifieren dat `none` statusregels onderdrukt, `light` hoofdacties toont en `verbose` playback-settings plus audio-bufferdetails toont.
- Traceability-tests verifieren `CHATOD-20260709-D1PY-MVP-001`, `Sprint 1 Kanban Backlog`, `EPIC-005 Configuratie En CLI`, `US-016 Debuglevel` en `Version: 0.1.0`.

## US-017: README Startinstructies

- Given een ontwikkelaar, when die README volgt, then setup, test-run, render command en play command duidelijk zijn.
- Given VS Code, then README verwijst naar debug-startpunt.

## US-018: Agile Artefacts

- Given Sprint 0, then MVP scope, user stories, acceptatiecriteria en Kanban backlog bestaan.
- Given het Kanban workbook, then stories met status, prioriteit, owner, story points en acceptatiecriteria samenvatting zichtbaar zijn.

## US-019: MIDI Leerpad En Terminologie

- Given de klant geen MIDI-protocolervaring heeft, when de MIDI sprint start, then er eerst uitleg is over note on/off, note number, velocity, channel, clock en pitch bend.
- Given een MIDI term wordt gebruikt in stories of code, then de README of docs een korte uitleg bevat.

Acceptatie op 2026-07-09:

- `docs/midi_learning_path_v0.1.0.md` bevat ChatOD, sprintnummer, doc versie, epic en `US-019 MIDI Leerpad En Terminologie`.
- De gids verklaart `note on`, `note off`, `note number`, `velocity`, `channel`, `MIDI clock` en `pitch bend`.
- De gids legt uit hoe MIDI later naar `NoteEvent` wordt gemapt.
- De gids noemt Logic Pro 12.3 en Arturia KeyLab Mk3 als toekomstige context.

## US-020: Virtual MIDI Input Voor DAW

- Given Logic Pro 12.3 of een andere DAW, when een virtual MIDI route beschikbaar is, then de DAW note events naar de synth kan sturen.
- Given MIDI note on/off events, then deze naar het bestaande `NoteEvent` model worden vertaald.
- Given de route niet beschikbaar is op het platform, then de CLI een duidelijke diagnose geeft.

Acceptatie op 2026-07-09:

- `MidiMessage` en `VirtualMidiInputAdapter` vertalen MIDI note-on/off paren naar `NoteSequence`.
- `note_on` met velocity `0` wordt als note-off behandeld.
- `python -m synth midi diagnose-virtual-input` geeft een duidelijke backenddiagnose zonder live CoreMIDI/RtMidi poort te openen.
- `docs/virtual_midi_input_v0.1.0.md` beschrijft de veilige DAW-route voor Logic Pro 12.3 en andere DAWs.
- Traceability-tests verifieren ChatOD, backlog, epic, `US-020 Virtual MIDI Input Voor DAW` en `Version: 0.1.0`.

## US-021: External MIDI Workflow In Logic

- Given Logic Pro 12.3, when de external MIDI workflow wordt onderzocht, then er een reproduceerbare setup-notitie ontstaat.
- Given een testnote vanuit Logic, then de synth een overeenkomstige note event ontvangt of de beperking wordt gedocumenteerd.

Acceptatie op 2026-07-09:

- `docs/logic_external_midi_workflow_v0.1.0.md` beschrijft een veilige Logic Pro 12.3 route via Audio MIDI Setup en IAC Driver.
- De workflow bevat een handmatige testtemplate voor de klant.
- Het Logic Pro/IAC testresultaat is ontvangen en vastgelegd.
- Er wordt geen live CoreMIDI/RtMidi inputpoort geopend in Python tijdens deze story.
- Geen hoorbaar geluid is verwacht in US-021; live MIDI receive en audio trigger horen bij een volgende story.

## US-022: USB MIDI Hardware Input

- Given een Arturia KeyLab Mk3, Fishman TriplePlay, M-Vave of ander USB MIDI input device, when het device zichtbaar is, then de CLI een generieke input-readiness diagnose kan geven.
- Given een device alleen output aanbiedt, then het niet als USB MIDI input-ready wordt beschouwd.
- Given een device naam of identifier wordt meegegeven, then de selectie op gedeeltelijke naam of identifier kan matchen.

Acceptatie op 2026-07-09:

- `UsbMidiHardwareInputAdapter` accepteert generieke MIDI input devices en is niet Arturia-only.
- `python -m synth midi diagnose-usb-input` geeft duidelijke diagnostiek.
- `docs/usb_midi_hardware_input_v0.1.0.md` bevat een handmatige hardwaretest-template.
- Elke MIDI hardwaretest start met device listing, daarna kiest de gebruiker een MIDI device of wijst een default device aan.
- Testresultaten leggen vast of ze op `KodeklopperM4` of `MuziekM4` zijn uitgevoerd.
- Als Logic Pro devices toont maar Python scanning faalt, wordt dat als apart scan/backend issue vastgelegd.
- De CLI toont backenddetails en `BLOCKER: Logic Pro shows MIDI devices but Python scan returned none.` wanneer Python geen MIDI devices vindt terwijl Logic Pro ze wel toont.
- De expliciete hardwaretest `PYTHON_D1_RUN_HARDWARE_MIDI=1 PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m pytest tests/test_hardware_midi.py -s` scant echte MIDI devices en faalt als er geen devices gevonden worden.
- Het package-conflict tussen `rtmidi 2.5.0` en `python-rtmidi 1.5.8` is vastgelegd als opgelost.
- `midi list-devices --unsafe-rtmidi-scan --debuglevel light` heeft op `KodeklopperM4` echte MIDI input- en outputdevices gelist.
- `SN76489 Synth Pappavis CircuitPython usb_midi.ports[0]` is vastgelegd als Lolin Wemos ESP32 S2 met CircuitPython 10 voor latere porting-context.
- US-022 is `Done` op basis van de succesvolle handmatige hardwaretest.

## US-023: Studio MIDI Routing Integratietest

- Given RaspiMidiHub, fysieke MIDI routing hub, MiniFreak en KeyLab Mk3, when de MIDI integratiesprint start, then er een testmatrix bestaat voor bron, route en bestemming.
- Given een routingpad wordt getest, then resultaat en eventuele latency/clock-beperkingen worden vastgelegd.
- Given een computer andere device-namen heeft, when MIDI routing wordt getest, then de route wordt gekozen via runtime MIDI device discovery en niet via hardcoded constants.
- Given KodeklopperM4 of MuziekM4 device scans worden gedocumenteerd, then deze als snapshots/placeholders worden behandeld.

Acceptatie op 2026-07-10:

- `docs/studio_midi_routing_integration_v0.1.0.md` bevat ChatOD, doc versie, epic en `US-023 Studio MIDI Routing Integratietest`.
- De routingmatrix dekt DAW virtual bus, USB MIDI interface, keyboard/controller, guitar MIDI, synth hardware, CircuitPython/ESP32, Windows `Spelen01` en Raspberry Pi 2.
- KodeklopperM4 en MuziekM4 device scans zijn vastgelegd als testdata.
- De documentatie zegt expliciet dat device-namen placeholders zijn en niet als constants in code mogen worden gebruikt.
- US-023 is `Done`.

## US-024: MIDI Naar NoteEvent Mapping

- Given een MIDI note on bericht, when de mapper draait, then note number, channel en velocity correct in een `NoteEvent` terechtkomen.
- Given een MIDI note off bericht, when de mapper draait, then het corresponderende interne event wordt beeindigd of als note-off event geregistreerd.
- Given toekomstige pitch bend en clock events, then het ontwerp uitbreidbaar blijft zonder de oscillator-engine te herschrijven.

Acceptatie op 2026-07-10:

- `MidiToNoteEventMapper` vertaalt `MidiMessage` note-on/off paren naar `NoteSequence`.
- MIDI note number 60 wordt intern `C4`.
- Velocity wordt genormaliseerd naar `0.0` tot en met `1.0`.
- `note_on` met velocity `0` wordt als note-off behandeld.
- Hetzelfde note number op verschillende channels wordt onafhankelijk gemapt.
- Ontbrekende note-off gebruikt een configureerbare default duration.
- `VirtualMidiInputAdapter` hergebruikt dezelfde mapper.
- `docs/midi_to_note_event_mapping_v0.1.0.md` bevat ChatOD, doc versie, epic en `US-024 MIDI Naar NoteEvent Mapping`.
- Traceability-tests verifieren ChatOD, backlog, epic, `US-024 MIDI Naar NoteEvent Mapping` en `Version: 0.1.0`.
- Er zijn geen hardcoded MIDI device names toegevoegd.

## US-025: MIDI Device Discovery En Default Selection

- Given USB, virtual of external MIDI devices beschikbaar zijn, when `python -m synth midi list-devices` draait, then de CLI een leesbare lijst met device naam, richting en stabiele selectie-identificatie toont.
- Given geen MIDI devices beschikbaar zijn, when de scan draait, then de CLI een duidelijke melding toont zonder crash.
- Given meerdere MIDI devices beschikbaar zijn, when de gebruiker `--midi-device` of `--midi-device-id` meegeeft, then de synth het gekozen input-device gebruikt.
- Given een YAML config met `midi.default_input_device`, when geen CLI override is opgegeven, then de synth de config-default gebruikt.
- Given zowel CLI device als YAML default bestaan, then de CLI keuze voorrang krijgt.
- Given een gekozen device niet gevonden wordt, then de CLI een duidelijke foutmelding toont met advies om opnieuw te scannen.
- Given macOS RtMidi/CoreMIDI scanning een native abort kan veroorzaken, then de CLI voert die scan niet standaard uit en vereist een expliciete unsafe diagnostic flag.

Acceptatie op 2026-07-10:

- `midi list-devices` toont `identifier`, `direction` en `name`.
- `--midi-device-id` selecteert exact op input identifier.
- `--midi-device` selecteert op input name fragment of identifier.
- `--config patch.yaml` leest `midi.default_input_device` wanneer geen CLI override is opgegeven.
- CLI wint van YAML default.
- Output devices worden niet als MIDI input geselecteerd.
- Onbekende input geeft een duidelijke melding met beschikbare input devices en advies om opnieuw te scannen.
- `--unsafe-rtmidi-scan` blijft vereist voor bewuste native RtMidi/CoreMIDI scanning op macOS.
- `docs/midi_device_discovery_default_selection_v0.1.0.md` bevat ChatOD, doc versie, epic en `US-025 MIDI Device Discovery En Default Selection`.
- Traceability-tests verifieren ChatOD, backlog, epic, `US-025 MIDI Device Discovery En Default Selection` en `Version: 0.1.0`.
- Er zijn geen hardcoded MIDI device names toegevoegd.

## US-026: Live MIDI Input Receive Loop

- Given een gekozen MIDI input device, when `midi listen` draait, then de command bounded luistert met `--max-messages` en `--timeout`.
- Given een backend note message, when de normalizer draait, then er een `MidiMessage` ontstaat met 1-based channel.
- Given een niet-note MIDI message, when US-026 draait, then het bericht wordt genegeerd.
- Given ontvangen note messages, when de receiver klaar is, then US-024 mapping een `NoteSequence` oplevert.
- Given hardwaretest nodig is, then de implementatie pauzeert voor klanttestresultaat.

Acceptatie op 2026-07-10:

- `MidiMessageNormalizer` ondersteunt note-on en note-off.
- `LiveMidiInputReceiver` gebruikt een fake backend in tests.
- `midi listen` selecteert input via US-025 selector.
- `midi listen` print ontvangen message count en gemapte sequence.
- `docs/live_midi_input_receive_loop_v0.1.0.md` bevat ChatOD, doc versie, epic en `US-026 Live MIDI Input Receive Loop`.
- Traceability-tests verifieren ChatOD, backlog, epic, `US-026 Live MIDI Input Receive Loop` en `Version: 0.1.0`.
- US-026 bevat geen Logic virtual device.
- US-026 bevat geen realtime audio-trigger.
- Er zijn geen hardcoded MIDI device names toegevoegd.
- Hardwaretest op `KodeklopperM4` is geslaagd met `SMK-37 Pro_BLE Bluetooth`.
- `--midi-device "MK-37 Pro_BLE"` selecteerde `input:7 SMK-37 Pro_BLE Bluetooth` en ontving 10 MIDI note messages.
- `--midi-device-id "input:7"` selecteerde hetzelfde device en ontving 4 MIDI note messages.
- De hardwaretest output bevat gemapte sequences zoals `C5@0.000s`, `B3@0.000s`, `B4@0.000s` en `A3@0.000s`.

## US-027: Virtual MIDI Port Voor Logic/DAW

- Given Logic Pro of een andere DAW, when de synth gestart wordt in virtual-port mode, then een MIDI destination zichtbaar kan worden.
- Given de DAW naar de virtual port routeert, then de synth MIDI note events kan ontvangen.
- Given macOS CoreMIDI/RtMidi beperkingen, then de implementatie veilig faalt met duidelijke diagnostiek.

Acceptatie op 2026-07-10:

- `midi virtual-port` opent een bounded virtual MIDI input port via `--name` en `--timeout`.
- `VirtualMidiPortSettings` valideert port name en timeout.
- `VirtualMidiPortManager` gebruikt een fake backend in unit tests.
- `MidoVirtualMidiPortBackend` gebruikt `mido.open_input(name, virtual=True)` alleen in de echte runtime route.
- CLI-fouten worden als `Virtual MIDI port error` gemeld.
- `docs/virtual_midi_port_logic_daw_v0.1.0.md` bevat ChatOD, doc versie, epic en `US-027 Virtual MIDI Port Voor Logic/DAW`.
- Traceability-tests verifieren ChatOD, backlog, epic, `US-027 Virtual MIDI Port Voor Logic/DAW` en `Version: 0.1.0`.
- US-027 bevat geen realtime audio-trigger; dit blijft US-028.
- Er zijn geen hardcoded MIDI device names toegevoegd.
- Logic Pro 12.3 handmatige zichtbaarheidstest is geslaagd op 2026-07-10 19:25.
- `python-d1-synth` is zichtbaar bij `Create New Track` > `MIDI` > `External MIDI` als MIDI destination.
- `python-d1-synth` is niet zichtbaar als Software Instrument / virtual instrument; dit is verwacht en valt buiten US-027.
- Story status is `Done`.

## US-028: External MIDI Audio Trigger Integratie

- Given ontvangen `NoteEvent` items, when live audio-triggering actief is, then de synth hoorbaar audio via de gekozen audio-output maakt.
- Given meerdere inputbronnen, then de audio-trigger dezelfde interne synth-engine gebruikt als CLI play/render.
- Given audio- of MIDI-backend faalt, then de CLI duidelijke troubleshooting output geeft.

Acceptatie op 2026-07-10:

- `midi play-live` luistert bounded naar een gekozen MIDI input en speelt ontvangen note events af.
- `MidiAudioTriggerSettings`, `MidiAudioTriggerResult` en `MidiAudioTrigger` zijn class-based en traceerbaar.
- De trigger gebruikt `LiveMidiInputReceiver`, `SynthEngine` en `SoundDeviceAudioPlayer`.
- CLI selectie gebruikt runtime MIDI device discovery via `--midi-device`, `--midi-device-id` of `--config`.
- CLI audio-output gebruikt `--audio-device`.
- Unit tests gebruiken een fake MIDI backend / fake receiver en fake audio player.
- CLI tests gebruiken fake scanner, fake audio selector en fake trigger.
- Er zijn geen hardcoded MIDI device names toegevoegd.
- US-028 bevat geen GUI, geen plugin, geen AU/VST3 en geen onbeperkte realtime performance-loop.
- `docs/external_midi_audio_trigger_v0.1.0.md` bevat ChatOD, doc versie, epic en `US-028 External MIDI Audio Trigger Integratie`.
- Traceability-tests verifieren ChatOD, backlog, epic, `US-028 External MIDI Audio Trigger Integratie` en `Version: 0.1.0`.
- Hoorbare hardwaretest is geslaagd op KodeklopperM4 met `SMK-37 Pro_BLE Bluetooth` naar `Scarlett 8i6 USB`.
- `midi play-live` rapporteerde `Played 8 MIDI-triggered note events from SMK-37 Pro_BLE Bluetooth.`
- De klant hoorde stereo geluid.
- De Logic Pro externe MIDI zichtbaarheidobservatie valt buiten US-028 en is geen blocker voor deze story.
- Story status is `Done`.

## US-029: Logic/DAW Virtual MIDI Naar Audio Trigger

- Given Logic Pro 12.3 of een andere DAW MIDI naar een virtual destination kan sturen, when `midi play-virtual` draait, then de synth een virtual MIDI input port opent en ontvangen note events hoorbaar afspeelt.
- Given de command draait, then de gebruiker `--port-name`, `--audio-device`, `--max-messages`, `--timeout`, `--waveform`, `--sample-rate`, `--channel` en `--debuglevel` kan instellen.
- Given Logic Pro wordt getest, then de documentatie expliciet `MIDI Destination: python-d1-synth`, `MIDI Channel: All` of `1`, en een korte MIDI region of Musical Typing als notenbron noemt.
- Given ontvangen note messages, then de bestaande US-024/US-026 mapping en US-028 audio-trigger route worden hergebruikt.
- Given Logic de destination niet ziet, then dit als virtual-port/DAW zichtbaarheidstest wordt behandeld en niet als plugin-issue.
- Given de gebruiker `Ctrl-C` indrukt, then de CLI netjes stopt met exit code `130` en een duidelijke onderbrekingsmelding.

Acceptatie op 2026-07-11:

- `midi play-virtual` bestaat als bounded command voor Logic/DAW virtual MIDI naar audio.
- `VirtualMidiAudioTriggerSettings`, `VirtualMidiAudioTriggerResult`, `MidoVirtualMidiInputBackend` en `VirtualMidiAudioTrigger` zijn class-based en traceerbaar.
- `MidoVirtualMidiInputBackend` gebruikt `mido.open_input(port_name, virtual=True)` alleen in de echte runtime route.
- Unit tests gebruiken een fake receiver en fake audio player.
- CLI tests gebruiken een fake virtual trigger en fake audio selector.
- CLI tests verifieren `KeyboardInterrupt` handling voor `midi play-virtual`.
- De aanbevolen Logic test gebruikt `--max-messages 2 --timeout 10`, omdat de MVP audio rendert nadat max-messages bereikt is of timeout afloopt.
- `docs/virtual_midi_audio_trigger_v0.1.0.md` bevat ChatOD, doc versie, epic en `US-029 Logic/DAW Virtual MIDI Naar Audio Trigger`.
- Traceability-tests verifieren ChatOD, backlog, epic, `US-029 Logic/DAW Virtual MIDI Naar Audio Trigger` en `Version: 0.1.0`.
- Geen GUI, geen plugin, geen AU/VST3, geen Logic Component en geen onbeperkte realtime performance-loop.
- Er zijn geen hardcoded MIDI hardware device names toegevoegd.
- Story status is `In Review` tot de handmatige Logic Pro test is bevestigd.
