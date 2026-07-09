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

### US-021: External MIDI Workflow In Logic

Als Logic Pro gebruiker wil ik een external MIDI workflow onderzoeken, zodat de synth in Logic of een andere DAW praktisch kan worden aangestuurd zonder direct een plugin te zijn.

Prioriteit: Should
Sprint: Future

### US-022: USB MIDI Hardware Input

Als gebruiker met een Arturia KeyLab Mk3 wil ik USB MIDI input kunnen ontvangen, zodat ik de synth met een fysiek MIDI keyboard kan bespelen.

Prioriteit: Must
Sprint: Future

### US-023: Studio MIDI Routing Integratietest

Als gebruiker met RaspiMidiHub, een fysieke MIDI routing hub, MiniFreak en KeyLab Mk3 wil ik een integratietestplan, zodat we later MIDI routing betrouwbaar kunnen testen.

Prioriteit: Should
Sprint: Future

### US-024: MIDI Naar NoteEvent Mapping

Als ontwikkelaar wil ik MIDI events naar het bestaande `NoteEvent` en `NoteSequence` model mappen, zodat de Sprint 1 synth-engine herbruikbaar blijft.

Prioriteit: Must
Sprint: Future

### US-025: MIDI Device Discovery En Default Selection

Als gebruiker wil ik via de commandline beschikbare USB, virtual en external MIDI devices kunnen scannen en een device kunnen kiezen, zodat ik de synth bewust met Logic, KeyLab Mk3, RaspiMidiHub of andere MIDI-bronnen kan verbinden.

Prioriteit: Must
Sprint: Future
