# python-d1-synth User Stories

ChatOD: CHATOD-20260709-D1PY-MVP-001 / ARTEFACTS-001
Datum: 2026-07-09
Status: Draft for customer review

## Rollen

- Klant: ervaren Python ontwikkelaar zonder MIDI/macOS/Windows audio-plugin ervaring.
- Product Owner: bewaakt MVP scope en prioriteiten.
- Lead Developer: bewaakt class based Python architectuur en testbaarheid.
- DSP Engineer: bewaakt audio- en syntheseconcepten.
- QA Engineer: bewaakt red/green testaanpak.
- Release Engineer: bewaakt VS Code, commandline en later GitHub workflow.

## Epic E1: Projectbasis

### US-001: Project Skeleton

Als ontwikkelaar wil ik een nette Python projectstructuur, zodat ik het project in VS Code en via commandline kan starten.

Prioriteit: Must
Sprint: 1

### US-002: Testframework

Als ontwikkelaar wil ik `pytest` ingericht hebben, zodat elke user story met red/green tests kan worden ontwikkeld.

Prioriteit: Must
Sprint: 1

### US-003: VS Code Debug Configuratie

Als ontwikkelaar wil ik een VS Code launch-config, zodat ik CLI commands in debug mode kan starten.

Prioriteit: Must
Sprint: 1

## Epic E2: Muzikale Basisdata

### US-004: Note Parsing

Als gebruiker wil ik noten zoals `C3` en `A4` kunnen invoeren, zodat de synth de juiste frequentie kan berekenen.

Prioriteit: Must
Sprint: 1

### US-005: Testsequence Parsing

Als gebruiker wil ik `--testsequence "ACGD"` kunnen invoeren, zodat ik snel een hoorbare reeks kan testen zonder muziektheorie te kennen.

Prioriteit: Must
Sprint: 1

### US-006: NoteEvent En NoteSequence Model

Als toekomstige MIDI-gebruiker wil ik een intern note-event model, zodat MIDI later naar dezelfde synth-engine gemapt kan worden.

Prioriteit: Must
Sprint: 1

Notitie: US-006 sluit het interne note-event model af met validatie, volgordebehoud, immutable sequence opslag en code traceability metadata.

## Epic E3: Oscillator En Audio Rendering

### US-007: Sine Oscillator

Als gebruiker wil ik een sine waveform kunnen genereren, zodat de eerste audio technisch bewijsbaar en eenvoudig testbaar is.

Prioriteit: Must
Sprint: 1

### US-008: Saw Oscillator

Als gebruiker wil ik een saw waveform kunnen genereren, zodat de synth richting subtractive synth karakter kan groeien.

Prioriteit: Should
Sprint: 1

Notitie: US-008 sluit saw waveform technisch af met sample count, amplitude, ramp-level tests en code traceability metadata.

### US-009: Square Oscillator

Als gebruiker wil ik een square waveform kunnen genereren, zodat ik een tweede klassieke monosynth waveform kan testen.

Prioriteit: Should
Sprint: 1

Notitie: US-009 sluit square waveform technisch af met sample count, amplitude, discrete-level tests en code traceability metadata.

### US-010: WAV Export

Als gebruiker wil ik een patch naar WAV kunnen renderen, zodat ik audio-output objectief kan inspecteren en bewaren.

Prioriteit: Must
Sprint: 1

Notitie: US-010 rondt WAV-export af met stereo PCM output, 44100 Hz patch-rendering en code traceability metadata.

## Epic E4: Realtime CLI Playback

### US-011: Play Single Note

Als gebruiker wil ik `python -m synth play --note C3` kunnen uitvoeren, zodat ik direct hoorbaar geluid krijg.

Prioriteit: Must
Sprint: 1

Notitie: voor macOS troubleshooting moet deze story ook `audio list-devices` en `--audio-device` ondersteunen, met `Scarlett 8i6 USB` als concrete klanttest.

### US-012: Play Testsequence

Als gebruiker wil ik `python -m synth play --testsequence "ACGD"` kunnen uitvoeren, zodat ik een simpele melodische test kan horen.

Prioriteit: Must
Sprint: 1

Notitie: deze story gebruikt de US-011 audio-device route, zodat `ACGD` ook expliciet via `Scarlett 8i6 USB` getest kan worden.

### US-013: Channel Selection

Als gebruiker wil ik `--channel stereo`, `--channel left` en `--channel right`, zodat ik audio-output routes kan testen.

Prioriteit: Must
Sprint: 1

Notitie: vanaf deze story moet geraakte code traceerbare metadata bevatten: ChatOD, backlog, epicnummer, user story nummer en versie.

## Epic E5: Configuratie En CLI

### US-014: YAML Patch Config

Als gebruiker wil ik patch-instellingen in YAML kunnen beschrijven, zodat synth parameters reproduceerbaar zijn.

Prioriteit: Must
Sprint: 1

### US-015: Render Command

Als gebruiker wil ik `python -m synth render patch.yaml --output demo.wav` kunnen uitvoeren, zodat ik een patch naar WAV kan renderen.

Prioriteit: Must
Sprint: 1

### US-016: Debuglevel

Als gebruiker wil ik `--debuglevel none|light|verbose`, zodat ik eenvoudige of uitgebreide CLI feedback kan kiezen.

Prioriteit: Should
Sprint: 1

Notitie: US-016 gebruikt code traceability metadata voor `DebugLevel`, `DebugReporter` en de CLI-entrypoint.

## Epic E6: Documentatie En Governance

### US-017: README Startinstructies

Als ontwikkelaar wil ik README-instructies, zodat ik setup, tests, CLI en debug workflow kan reproduceren.

Prioriteit: Must
Sprint: 1

### US-018: Agile Artefacts

Als klant wil ik MVP scope, user stories, acceptatiecriteria en Kanban backlog, zodat ik het werk als vendor-traject kan volgen.

Prioriteit: Must
Sprint: 0

## Epic E7: Future MIDI En DAW Integratie

### US-019: MIDI Leerpad En Terminologie

Als klant zonder MIDI-protocolervaring wil ik een begeleid MIDI-leerpad, zodat ik note on/off, channels, velocity, clock en pitch bend begrijp voordat we hardware of DAW-integratie bouwen.

Prioriteit: Must
Sprint: Future

Notitie: US-019 is afgerond met `docs/midi_learning_path_v0.1.0.md`, inclusief kernbegrippen, mapping naar `NoteEvent`, Logic Pro 12.3 context en Arturia KeyLab Mk3 context.

### US-020: Virtual MIDI Input Voor DAW

Als Logic Pro 12.3 gebruiker wil ik de synth later via een virtual MIDI input kunnen bespelen, zodat Logic of een andere DAW note events naar de Python synth kan sturen.

Prioriteit: Must
Sprint: Future

Notitie: US-020 is afgerond met `VirtualMidiInputAdapter`, MIDI note-on/off naar `NoteSequence` mapping, CLI-diagnose `midi diagnose-virtual-input`, en `docs/virtual_midi_input_v0.1.0.md`.

### US-021: External MIDI Workflow In Logic

Als Logic Pro gebruiker wil ik een external MIDI workflow onderzoeken, zodat de synth in Logic of een andere DAW praktisch kan worden aangestuurd zonder direct een plugin te zijn.

Prioriteit: Should
Sprint: Future

Notitie: US-021 is afgerond met `docs/logic_external_midi_workflow_v0.1.0.md`; het handmatige Logic/IAC testresultaat is ontvangen en geen geluid was verwacht voor deze story.

### US-022: USB MIDI Hardware Input

Als gebruiker met Arturia KeyLab Mk3, Fishman TriplePlay, M-Vave of een ander USB MIDI input device wil ik hardware input kunnen diagnosticeren, zodat de synth niet aan een specifiek merk of controller vastzit.

Prioriteit: Must
Sprint: Future

Notitie: US-022 is Done. Het package-conflict tussen `rtmidi 2.5.0` en `python-rtmidi 1.5.8` is opgelost, waarna `midi list-devices --unsafe-rtmidi-scan --debuglevel light` in een gewone Terminal op `KodeklopperM4` echte MIDI input- en outputdevices liste. De succesvolle test bevat onder meer `Scarlett 8i6 USB`, `SMK-37 Pro_BLE Bluetooth` en `SN76489 Synth Pappavis CircuitPython usb_midi.ports[0]`, waarbij de SN76489 een Lolin Wemos ESP32 S2 met CircuitPython 10 is voor latere porting-context.

### US-023: Studio MIDI Routing Integratietest

Als gebruiker met RaspiMidiHub, een fysieke MIDI routing hub, MiniFreak en KeyLab Mk3 wil ik een integratietestplan, zodat we later MIDI routing betrouwbaar kunnen testen.

Prioriteit: Should
Sprint: Future

Notitie: US-023 is Done met `docs/studio_midi_routing_integration_v0.1.0.md`. De testmatrix dekt DAW virtual bus, USB MIDI interface, keyboard/controller, guitar MIDI, synth hardware, CircuitPython/ESP32, Windows `Spelen01` en Raspberry Pi 2. Device-namen uit KodeklopperM4 en MuziekM4 zijn snapshots/placeholders en mogen niet als constants in code worden vastgelegd.

### US-024: MIDI Naar NoteEvent Mapping

Als ontwikkelaar wil ik MIDI events naar het bestaande `NoteEvent` en `NoteSequence` model mappen, zodat de Sprint 1 synth-engine herbruikbaar blijft.

Prioriteit: Must
Sprint: Future

Notitie: US-024 is Done met `MidiToNoteEventMapper` en `docs/midi_to_note_event_mapping_v0.1.0.md`. De mapper vertaalt `MidiMessage` note-on/off paren naar `NoteEvent`, behandelt `note_on` met velocity 0 als note-off, houdt channels gescheiden en gebruikt default duration bij ontbrekende note-off. Er zijn geen hardcoded MIDI device names toegevoegd.

### US-025: MIDI Device Discovery En Default Selection

Als gebruiker wil ik via de commandline beschikbare USB, virtual en external MIDI devices kunnen scannen en een device kunnen kiezen, zodat ik de synth bewust met Logic, KeyLab Mk3, RaspiMidiHub of andere MIDI-bronnen kan verbinden.

Prioriteit: Must
Sprint: Future

Notitie: US-025 is Done met `MidiDeviceSelector`, `MidiDeviceSelection`, CLI flags `--midi-device`, `--midi-device-id` en `--config`, plus `docs/midi_device_discovery_default_selection_v0.1.0.md`. CLI selectie wint van YAML default, output devices worden niet als input gekozen en er zijn geen hardcoded MIDI device names toegevoegd.

### US-026: Live MIDI Input Receive Loop

Als gebruiker wil ik de commandline synth bounded naar een gekozen MIDI input kunnen laten luisteren, zodat inkomende note messages veilig naar het interne `MidiMessage` en `NoteSequence` model worden vertaald.

Prioriteit: Must
Sprint: Future

Notitie: US-026 is Done met `LiveMidiInputReceiver`, `MidiMessageNormalizer`, `MidiInputReceiveSettings`, `MidiInputReceiveResult`, CLI command `midi listen`, fake-backend tests en `docs/live_midi_input_receive_loop_v0.1.0.md`. De hardwaretest op `KodeklopperM4` is geslaagd met `SMK-37 Pro_BLE Bluetooth` via naamfragment en `input:7`. Deze story doet nog geen Logic virtual device en geen realtime audio-trigger.

### US-027: Virtual MIDI Port Voor Logic/DAW

Als Logic Pro of DAW gebruiker wil ik dat `python-d1-synth` als virtual MIDI destination zichtbaar kan worden, zodat een DAW MIDI naar de Python synth kan sturen zonder hardware-driver.

Prioriteit: Should
Sprint: Future

Notitie: Done met `VirtualMidiPortSettings`, `VirtualMidiPortResult`, `MidoVirtualMidiPortBackend`, `VirtualMidiPortManager`, CLI command `midi virtual-port`, fake-backend tests en `docs/virtual_midi_port_logic_daw_v0.1.0.md`. De Logic Pro 12.3 klanttest is geslaagd: `python-d1-synth` is beschikbaar als External MIDI destination. Niet zichtbaar als Software Instrument / virtual instrument is verwacht en valt buiten US-027. Realtime audio-triggering blijft US-028.

### US-028: External MIDI Audio Trigger Integratie

Als gebruiker wil ik ontvangen MIDI note events hoorbaar via de Mac audio-output kunnen triggeren, zodat een hardware controller, DAW route of externe MIDI route de synth live kan bespelen.

Prioriteit: Must
Sprint: Future

Notitie: Done met `MidiAudioTriggerSettings`, `MidiAudioTriggerResult`, `MidiAudioTrigger`, CLI command `midi play-live`, fake MIDI backend tests, fake audio player tests en `docs/external_midi_audio_trigger_v0.1.0.md`. De klanttest is geslaagd op KodeklopperM4: `SMK-37 Pro_BLE Bluetooth` triggerde hoorbaar stereo geluid via `Scarlett 8i6 USB`. De Logic Pro externe MIDI zichtbaarheidobservatie blijft buiten US-028.

### US-029: Logic/DAW Virtual MIDI Naar Audio Trigger

Als Logic Pro of DAW gebruiker wil ik `python-d1-synth` als virtual MIDI destination kunnen starten en direct hoorbare audio kunnen triggeren, zodat een DAW MIDI naar de Python synth kan sturen zonder plugin.

Prioriteit: Must
Sprint: Future

Notitie: Done met `MidoVirtualMidiInputBackend`, `VirtualMidiAudioTriggerSettings`, `VirtualMidiAudioTriggerResult`, `VirtualMidiAudioTrigger`, CLI command `midi play-virtual`, fake receiver tests, fake audio player tests en `docs/virtual_midi_audio_trigger_v0.1.0.md`. De Logic Pro test is geslaagd: een MIDI region stuurde `note_on:60:velocity=50:channel=1` naar `python-d1-synth` en er was hoorbaar geluid via `Scarlett 8i6 USB`. Deze story combineert US-027 virtual port zichtbaarheid met US-028 audio-triggering. Geen GUI, geen plugin, geen AU/VST3 en geen hardcoded MIDI hardware device names.

### US-030: Logic MIDI Region Multi-Note Playback

Als Logic Pro of DAW gebruiker wil ik een korte MIDI region met meerdere noten naar `python-d1-synth` kunnen sturen, zodat de batch-route meer dan één ontvangen noot hoorbaar kan renderen.

Prioriteit: Must
Sprint: Future

Notitie: Done met multi-note MIDI mapping tests, `VirtualMidiAudioTriggerResult.played_events`, verbose CLI output voor `Rendered sequence events`, en `docs/logic_midi_region_multi_note_playback_v0.1.0.md`. Product Owner test bevestigde hoorbare multi-note Logic playback: `Played 5 MIDI-triggered note events` en `Rendered sequence events: C4@0.945s, F4@1.062s, F4@1.560s, C4@1.960s, F4@2.200s`. Scope blijft batchgewijs: audio speelt nadat `--max-messages` bereikt is of `--timeout` afloopt. Realtime streaming, pitch bend en modulation blijven buiten US-030.

### US-031: Live/Streaming MIDI Playback Loop

Als Logic Pro of DAW gebruiker wil ik dat ontvangen MIDI `note_on` events direct hoorbaar worden afgespeeld, zodat de vertraging uit de US-030 batchroute merkbaar lager wordt.

Prioriteit: Must
Sprint: Future

Notitie: Done met `StreamingMidiAudioTriggerSettings`, `StreamingMidiAudioTriggerResult`, `MidoStreamingVirtualMidiInputBackend`, `StreamingMidiAudioTrigger`, CLI command `midi play-stream`, fake streaming-backend tests en `docs/live_streaming_midi_playback_loop_v0.1.0.md`. Product Owner test bevestigde realtime playback: `Streamed 18 MIDI-triggered note events`. De test toonde ook dubbele MIDI events; dat is US-032. Scope: near-realtime fixed-duration note playback. Geen pitch bend, modulation, sustain, polyfonie, GUI, AU/VST3 of professionele low-latency audio engine.

### US-032: Duplicate MIDI Event Guard

Als gebruiker wil ik dat dubbele MIDI note events uit Logic/routing niet dubbel hoorbaar worden afgespeeld, zodat een enkele noot niet als twee kort na elkaar komende noten klinkt.

Prioriteit: Must
Sprint: Future

Notitie: Done met `DuplicateMidiEventGuardSettings`, `DuplicateMidiEventGuard`, `StreamingMidiAudioTriggerSettings.dedupe_window_seconds`, CLI optie `--dedupe-window`, verbose duplicate diagnostics en `docs/duplicate_midi_event_guard_v0.1.0.md`. Product Owner test bevestigde hoorbaar geluid vanuit Logic en live note playback: `Streamed 6 MIDI-triggered note events` en `suppressed 23 duplicate MIDI messages`. Identieke `note_on`/`note_off` echo-events binnen de window worden onderdrukt; verschillende noten op dezelfde timestamp blijven behouden als voorbereiding op US-034 polyfonie/triads. Kleine latency blijft voor latere stories. Geen note-off gated duration, sustain, pitch bend, modulation of volledige polyfonie binnen US-032.

### US-033: Note Off Gated Voice Duration

Als speler wil ik dat note-on en note-off samen de hoorbare nootlengte bepalen, zodat korte en lange gespeelde noten muzikaal correcter reageren dan fixed-duration playback.

Prioriteit: Must
Sprint: Future

Notitie: Done met `StreamingVoiceMode`, `StreamingMidiAudioTriggerSettings.voice_mode`, CLI optie `--voice-mode gated`, gated note-on/note-off duration tests en `docs/note_off_gated_voice_duration_v0.1.0.md`. Product Owner test bevestigde hoorbaar geluid en accepteerde dat US-033 een pulse + duration-reporting tussenstap is. Default blijft `--voice-mode fixed` zodat US-031/US-032 niet breken. Scope: monofone/parallel note-on/off duurmeting per MIDI key binnen bounded CLI playback. Geen sustain pedal, envelope release, polyfonie mixer, pitch bend, modulation, GUI of plugin.

### US-034: Polyphonic Voice Mixer En Triads

Als speler wil ik meerdere gelijktijdige noten kunnen horen, zodat triads en akkoorden mogelijk worden.

Prioriteit: Must
Sprint: Future

Notitie: Done met `PolyphonicVoiceMixer`, streaming MIDI poll-batches, CLI optie `--chord-window`, triad batch tests en `docs/polyphonic_voice_mixer_triads_v0.1.0.md`. Product Owner test bevestigde akkoordachtige groepen met `--chord-window 0.08`. De story mixt gelijktijdige note-on events als akkoordbuffer, terwijl duplicate filtering verschillende chord tones behoudt. Scope: polyphonic fixed/fallback buffers; geen echte sustained voice engine, pitch bend, modulation, GUI of plugin.

### US-035: Sustained Note Audio Engine

Als speler wil ik dat note-on een hoorbare voice start en note-off die voice stopt, zodat een vastgehouden toets niet als kort pulse-nootje klinkt.

Prioriteit: Must
Sprint: Future

Notitie: Done met `SoundDeviceSustainedAudioPlayer`, `SustainedAudioPlayerSettings`, `SustainedVoiceState`, `StreamingVoiceMode.SUSTAINED`, CLI optie `--voice-mode sustained` en `docs/sustained_note_audio_engine_v0.1.0.md`. Product Owner test bevestigde sustained playback met `Total streamed audio frames: 575172`. Scope: sustained note-on/note-off voice lifecycle; geen sustain pedal, envelope release, pitch bend, modulation, GUI of plugin.

### US-036: MIDI Pitch Bend Mapping En DSP

Als speler wil ik MIDI pitch bend kunnen gebruiken, zodat gespeelde noten vloeiend omhoog of omlaag kunnen buigen.

Prioriteit: Should
Sprint: Future

Notitie: Done met `MidiPitchBendMapper`, `MidiMessage(message_type="pitch_bend")`, mido `pitchwheel` normalisatie, `SoundDeviceSustainedAudioPlayer.pitch_bend(...)`, CLI opties `--pitch-bend-range`, `--pitch-bend-channel-mode same|omni`, `--max-control-messages` en `docs/midi_pitch_bend_mapping_dsp_v0.1.0.md`. Product Owner accepteerde hoorbare sustained playback, triads en korte/lange nootduur; `Ctrl-C` stopt de langere sessie. Scope: pitch bend op sustained voices; geen sustain pedal, envelope release, GUI of plugin.

### US-037: MIDI Modulation CC1 Mapping En DSP

Als speler wil ik MIDI modulation kunnen gebruiken, zodat CC1 later vibrato, filter of andere modulatie kan aansturen.

Prioriteit: Should
Sprint: Future

Notitie: Done met `MidiMessage(message_type="control_change")`, mido `control_change` normalisatie, `MidiModulationMapper`, `SoundDeviceSustainedAudioPlayer.modulation(...)`, CLI opties `--modulation-vibrato-depth` en `--modulation-vibrato-rate`, plus `docs/midi_modulation_cc1_mapping_dsp_v0.1.0.md`. Product Owner accepteerde hoorbare pitch bend/CC1 modulation en de interrupt-fix. Scope: CC1 stuurt eenvoudige vibrato-depth; geen filter, sustain pedal, envelope release, GUI of plugin.

### US-038: Performance Mode Until Interrupt

Als speler wil ik `midi play-stream` kunnen starten zonder korte testlimiet, zodat ik de synth gewoon kan bespelen tot ik zelf met `Ctrl-C` stop.

Prioriteit: Must
Sprint: Future

Notitie: Done met CLI optie `--until-interrupt`, `StreamingMidiAudioTriggerSettings.run_until_interrupted`, praktische lange backend-limieten, verbose `until_interrupt=true` diagnostics en `docs/performance_mode_until_interrupt_v0.1.0.md`. Product Owner testte US-038 als geslaagd. Scope: performance-mode voor bestaande commandline streaming; geen envelope release, GUI of plugin.

### US-039: Sustain Pedal CC64

Als speler wil ik MIDI sustain pedal kunnen gebruiken, zodat notes blijven klinken nadat ik toetsen loslaat zolang de pedal ingedrukt is.

Prioriteit: Must
Sprint: Future

Notitie: Done met `control_change:64` handling in `--voice-mode sustained`, CC64 threshold `64`, held-voice release bij pedal up, verbose diagnostics en `docs/sustain_pedal_cc64_v0.1.0.md`. Product Owner heeft geen fysieke sustain pedal en accepteerde US-039 op basis van aanname plus groene automatische CC64-tests. Scope: geen half-pedal curves, geen envelope release, geen sostenuto pedal, GUI of plugin.

### US-040: Envelope Release / Soft Note-Off

Als speler wil ik dat note-off niet hard wordt afgekapt, zodat sustained notes natuurlijker stoppen en minder click-achtig klinken.

Prioriteit: Should
Sprint: Future

Notitie: Done met `SustainedAudioPlayerSettings.release_seconds`, release frames in `SustainedVoiceState`, CLI optie `--release-time`, audio callback fade-out tests en `docs/envelope_release_soft_note_off_v0.1.0.md`. Product Owner accepteerde US-040 op 2026-07-12. Default is `--release-time 0.03`; `--release-time 0` herstelt hard-stop gedrag voor vergelijking. Scope: geen volledige ADSR envelope, geen filter envelope, GUI of plugin.

### US-041: Amp Envelope ADSR Parameters

Als speler wil ik attack, decay, sustain en release voor amplitude kunnen instellen, zodat sustained notes minder statisch klinken en patch-karakter krijgen.

Prioriteit: Should
Sprint: Future

Notitie: Done met `SustainedAudioPlayerSettings.attack_seconds`, `decay_seconds`, `sustain_level`, bestaande `release_seconds`, CLI opties `--attack-time`, `--decay-time`, `--sustain-level`, `--release-time`, audio callback envelope tests en `docs/amp_envelope_adsr_parameters_v0.1.0.md`. Product Owner accepteerde US-041 op 2026-07-13. Scope: geen filter envelope, geen velocity-afhankelijke envelope curves, GUI of plugin.

### US-042: MIDI Performance Patch YAML Config

Als speler wil ik `midi play-stream` performance parameters uit een YAML patch kunnen laden, zodat ik de synth met een kort reproduceerbaar command kan starten zonder steeds alle live flags over te typen.

Prioriteit: Should
Sprint: Future

Notitie: Done met `MidiPerformanceConfig`, `midi.performance` in YAML, CLI optie `midi play-stream --config`, voorbeeldbestand `examples/midi_performance_patch.yaml`, CLI precedence tests en `docs/midi_performance_patch_yaml_config_v0.1.0.md`. Expliciete CLI flags winnen van YAML, zodat testcommands en live overrides veilig blijven. Product Owner testte op 2026-07-14 dat Logic MIDI naar `python-d1-synth` stuurt en er hoorbaar geluid via `Scarlett 8i6 USB` is. Scope: geen GUI, geen AU/VST3/plugin packaging, geen hardcoded MIDI hardware device names.
