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

## US-007: Sine Oscillator

- Given frequentie, duur en sample rate, when de sine oscillator samples genereert, then het aantal samples klopt.
- Given amplitude-limieten, then samples binnen `-1.0` en `1.0` blijven.
- Given een vaste input, then output deterministisch testbaar is.

## US-008: Saw Oscillator

- Given frequentie, duur en sample rate, when de saw oscillator samples genereert, then het aantal samples klopt.
- Given amplitude-limieten, then samples binnen `-1.0` en `1.0` blijven.

## US-009: Square Oscillator

- Given frequentie, duur en sample rate, when de square oscillator samples genereert, then het aantal samples klopt.
- Given amplitude-limieten, then samples binnen `-1.0` en `1.0` blijven.

## US-010: WAV Export

- Given een patch-config, when `render patch.yaml --output demo.wav` draait, then `demo.wav` wordt aangemaakt.
- Given stereo output, then het WAV-bestand twee kanalen bevat.
- Given sample rate `44100`, then het WAV-bestand die sample rate gebruikt.

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

## US-017: README Startinstructies

- Given een ontwikkelaar, when die README volgt, then setup, test-run, render command en play command duidelijk zijn.
- Given VS Code, then README verwijst naar debug-startpunt.

## US-018: Agile Artefacts

- Given Sprint 0, then MVP scope, user stories, acceptatiecriteria en Kanban backlog bestaan.
- Given het Kanban workbook, then stories met status, prioriteit, owner, story points en acceptatiecriteria samenvatting zichtbaar zijn.

## US-019: MIDI Leerpad En Terminologie

- Given de klant geen MIDI-protocolervaring heeft, when de MIDI sprint start, then er eerst uitleg is over note on/off, note number, velocity, channel, clock en pitch bend.
- Given een MIDI term wordt gebruikt in stories of code, then de README of docs een korte uitleg bevat.

## US-020: Virtual MIDI Input Voor DAW

- Given Logic Pro 12.3 of een andere DAW, when een virtual MIDI route beschikbaar is, then de DAW note events naar de synth kan sturen.
- Given MIDI note on/off events, then deze naar het bestaande `NoteEvent` model worden vertaald.
- Given de route niet beschikbaar is op het platform, then de CLI een duidelijke diagnose geeft.

## US-021: External MIDI Workflow In Logic

- Given Logic Pro 12.3, when de external MIDI workflow wordt onderzocht, then er een reproduceerbare setup-notitie ontstaat.
- Given een testnote vanuit Logic, then de synth een overeenkomstige note event ontvangt of de beperking wordt gedocumenteerd.

## US-022: USB MIDI Hardware Input

- Given een Arturia KeyLab Mk3 via USB MIDI, when een toets wordt ingedrukt, then de synth een note on event ontvangt.
- Given de toets wordt losgelaten, then de synth een note off event ontvangt.
- Given velocity wordt meegestuurd, then de waarde in het interne eventmodel zichtbaar is.

## US-023: Studio MIDI Routing Integratietest

- Given RaspiMidiHub, fysieke MIDI routing hub, MiniFreak en KeyLab Mk3, when de MIDI integratiesprint start, then er een testmatrix bestaat voor bron, route en bestemming.
- Given een routingpad wordt getest, then resultaat en eventuele latency/clock-beperkingen worden vastgelegd.

## US-024: MIDI Naar NoteEvent Mapping

- Given een MIDI note on bericht, when de mapper draait, then note number, channel en velocity correct in een `NoteEvent` terechtkomen.
- Given een MIDI note off bericht, when de mapper draait, then het corresponderende interne event wordt beeindigd of als note-off event geregistreerd.
- Given toekomstige pitch bend en clock events, then het ontwerp uitbreidbaar blijft zonder de oscillator-engine te herschrijven.

## US-025: MIDI Device Discovery En Default Selection

- Given USB, virtual of external MIDI devices beschikbaar zijn, when `python -m synth midi list-devices` draait, then de CLI een leesbare lijst met device naam, richting en stabiele selectie-identificatie toont.
- Given geen MIDI devices beschikbaar zijn, when de scan draait, then de CLI een duidelijke melding toont zonder crash.
- Given meerdere MIDI devices beschikbaar zijn, when de gebruiker `--midi-device` of `--midi-device-id` meegeeft, then de synth het gekozen input-device gebruikt.
- Given een YAML config met `midi.default_input_device`, when geen CLI override is opgegeven, then de synth de config-default gebruikt.
- Given zowel CLI device als YAML default bestaan, then de CLI keuze voorrang krijgt.
- Given een gekozen device niet gevonden wordt, then de CLI een duidelijke foutmelding toont met advies om opnieuw te scannen.
- Given macOS RtMidi/CoreMIDI scanning een native abort kan veroorzaken, then de CLI voert die scan niet standaard uit en vereist een expliciete unsafe diagnostic flag.
