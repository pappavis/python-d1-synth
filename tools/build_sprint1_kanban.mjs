import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "../outputs/CHATOD-20260709-D1PY-MVP-001";
await fs.mkdir(outputDir, { recursive: true });

const workbook = Workbook.create();
const board = workbook.worksheets.add("Sprint 1 Board");
const future = workbook.worksheets.add("Future MIDI DAW");
const summary = workbook.worksheets.add("Summary");
const ref = workbook.worksheets.add("Reference");

const stories = [
  ["US-001", "Story", "Projectbasis", "Project Skeleton", "Done", "Must", "Lead Developer", 3, "Sprint 1", "Project startbaar via CLI en VS Code debug.", "Test import/start faalt voor skeleton.", "Minimal package layout en entrypoint.", "None", "src package, pyproject en CLI skeleton gemaakt."],
  ["US-002", "Story", "Projectbasis", "Testframework", "Done", "Must", "QA Engineer", 2, "Sprint 1", "pytest start zonder importfouten.", "pytest faalt zonder tests/setup.", "pytest configuratie en eerste smoke test.", "US-001", "pytest draait groen: 9 passed."],
  ["US-003", "Story", "Projectbasis", "VS Code Debug Configuratie", "Done", "Must", "Release Engineer", 2, "Sprint 1", "CLI command debugbaar in VS Code.", "Debug config ontbreekt.", "launch.json met play/render voorbeelden.", "US-001", "launch.json en settings.json toegevoegd."],
  ["US-004", "Story", "Muzikale Basisdata", "Note Parsing", "Done", "Must", "Lead Developer", 3, "Sprint 1", "C3 en A4 worden correct naar frequentie gemapt.", "C3/A4 tests falen.", "NoteParser class met validatie.", "US-001, US-002", "pytest dekt A4 en C3 frequenties."],
  ["US-005", "Story", "Muzikale Basisdata", "Testsequence Parsing", "Done", "Must", "Lead Developer", 3, "Sprint 1", "ACGD wordt A3 C4 G3 D4.", "Sequence parser test faalt.", "NoteSequence parser met defaults.", "US-004", "pytest dekt ACGD default octaves."],
  ["US-006", "Story", "Muzikale Basisdata", "NoteEvent En NoteSequence Model", "Done", "Must", "DSP Engineer", 3, "Sprint 1", "Intern eventmodel ondersteunt note, duration, velocity, timing en traceerbare code-docstrings.", "Modelvalidatie en traceability tests falen.", "NoteEvent validatie, NoteSequence tuple-normalisatie en code traceability.", "US-004", "pytest groen: duration, velocity, timing, volgorde en traceability afgedekt."],
  ["US-007", "Story", "Oscillator En Audio Rendering", "Sine Oscillator", "Done", "Must", "DSP Engineer", 5, "Sprint 1", "Sine samples hebben juiste lengte en amplitude.", "Sample count/amplitude tests falen.", "SineOscillator class met numpy.", "US-006", "pytest dekt sample count en amplitude."],
  ["US-008", "Story", "Oscillator En Audio Rendering", "Saw Oscillator", "Done", "Should", "DSP Engineer", 3, "Sprint 1", "Saw samples hebben juiste lengte, amplitude en ramp-niveaus met traceerbare code-docstrings.", "Saw oscillator en traceability tests falen.", "Oscillator ondersteunt saw met meerdere ramp-niveaus binnen amplitude.", "US-007", "pytest groen: saw count, amplitude, ramp levels en traceability afgedekt."],
  ["US-009", "Story", "Oscillator En Audio Rendering", "Square Oscillator", "Done", "Should", "DSP Engineer", 3, "Sprint 1", "Square samples hebben juiste lengte, amplitude en discrete niveaus met traceerbare code-docstrings.", "Square oscillator en traceability tests falen.", "Oscillator ondersteunt square met discrete -amplitude/+amplitude output.", "US-007", "pytest groen: square count, amplitude, levels en traceability afgedekt."],
  ["US-010", "Story", "Oscillator En Audio Rendering", "WAV Export", "Done", "Must", "Lead Developer", 5, "Sprint 1", "Render command schrijft stereo WAV op 44100 Hz.", "WAV bestandsinspectie faalt.", "WaveWriter class met standaard wave module.", "US-007", "CLI render maakte outputs/demo.wav met 2 kanalen, 44100 Hz, 44100 frames."],
  ["US-011", "Story", "Realtime CLI Playback", "Play Single Note", "Done", "Must", "Lead Developer", 5, "Sprint 1", "play --note C3 maakt hoorbaar geluid en kan --audio-device gebruiken.", "Audio output adapter en CLI parsing tests falen.", "sounddevice adapter, audio list-devices, --audio-device en Scarlett testdocs.", "US-007", "Klanttest geslaagd: hoorbaar geluid via Scarlett 8i6 USB."],
  ["US-012", "Story", "Realtime CLI Playback", "Play Testsequence", "Done", "Must", "Lead Developer", 3, "Sprint 1", "play --testsequence ACGD speelt vier noten en ondersteunt --audio-device.", "Sequence playback test faalt.", "Playback engine voor NoteSequence plus CLI verbose eventdiagnose.", "US-005, US-011", "Klanttest geslaagd: ACGD sequence hoorbaar via Scarlett 8i6 USB."],
  ["US-013", "Story", "Realtime CLI Playback", "Channel Selection", "Done", "Must", "QA Engineer", 3, "Sprint 1", "stereo/left/right kanaalrouting werkt met traceerbare code-docstrings.", "Kanaalrouting en traceability tests falen.", "ChannelRouter, SynthEngine en CLI tests voor stereo/left/right plus code traceability.", "US-010, US-011", "Klanttest geslaagd: stereo, left en right hoorbaar via Scarlett 8i6 USB."],
  ["US-014", "Story", "Configuratie En CLI", "YAML Patch Config", "Done", "Must", "Lead Developer", 3, "Sprint 1", "Patch YAML laadt oscillator, duration, sample_rate en channel.", "Patch loader tests falen.", "PatchConfig class en loader.", "US-007", "PyYAML loader, example patch en config test toegevoegd."],
  ["US-015", "Story", "Configuratie En CLI", "Render Command", "Done", "Must", "Lead Developer", 3, "Sprint 1", "render patch.yaml --output demo.wav schrijft WAV.", "CLI render test faalt.", "argparse command en render workflow.", "US-010, US-014", "CLI render succesvol geverifieerd."],
  ["US-016", "Story", "Configuratie En CLI", "Debuglevel", "Done", "Should", "QA Engineer", 2, "Sprint 1", "none/light/verbose tonen juiste hoeveelheid output met traceerbare code-docstrings.", "DebugReporter, CLI output en traceability tests falen.", "DebugLevel, DebugReporter en CLI output tests voor none/light/verbose.", "US-011, US-015", "pytest groen: none onderdrukt status, light toont hoofdacties, verbose toont technische details."],
  ["US-017", "Story", "Documentatie En Governance", "README Startinstructies", "Done", "Must", "Technical Writer", 2, "Sprint 1", "README beschrijft setup, test, play, render en debug.", "Docs review checklist faalt.", "README update na skeleton.", "US-001", "README bijgewerkt met venv, CLI, tests en VS Code."],
  ["US-018", "Story", "Documentatie En Governance", "Agile Artefacts", "Done", "Must", "Product Owner", 2, "Sprint 0", "Scope, stories, criteria en Kanban workbook bestaan.", "Artefact checklist faalt.", "Markdown docs en Excel Kanban genereren.", "None", "Artefacts en workbook bijgewerkt."],
];

const headers = [
  "ID",
  "Type",
  "Epic",
  "Title",
  "Status",
  "Priority",
  "Owner",
  "Story Points",
  "Sprint",
  "Acceptance Criteria Summary",
  "Red Phase Test",
  "Green Phase Work",
  "Dependencies",
  "Notes",
];

const futureStories = [
  ["US-019", "Story", "Future MIDI En DAW Integratie", "MIDI Leerpad En Terminologie", "Done", "Must", "Product Owner", 2, "Future", "Klant begrijpt note on/off, note number, channel, velocity, MIDI clock en pitch bend.", "Docs ontbreken voor MIDI basisbegrippen.", "MIDI concept guide en glossary met NoteEvent mapping.", "US-006", "docs/midi_learning_path_v0.1.0.md en pytest docs-check groen."],
  ["US-020", "Story", "Future MIDI En DAW Integratie", "Virtual MIDI Input Voor DAW", "Done", "Must", "Lead Developer", 5, "Future", "Logic Pro 12.3 of andere DAW heeft veilige virtual MIDI input voorbereiding en note-event mapping.", "Virtual MIDI adapter, CLI diagnose en traceability tests falen.", "VirtualMidiInputAdapter, MidiMessage en midi diagnose-virtual-input.", "US-006, US-019", "pytest groen: note on/off mapping, velocity zero note-off, CLI diagnose en traceability."],
  ["US-021", "Story", "Future MIDI En DAW Integratie", "External MIDI Workflow In Logic", "Done", "Should", "Release Engineer", 3, "Future", "External MIDI workflow in Logic is reproduceerbaar beschreven en klanttest is vastgelegd.", "Logic external MIDI setup test faalt of ontbreekt.", "Logic/IAC workflowdoc en handmatige testresultaatregistratie.", "US-020", "Klanttest geslaagd: IAC route zichtbaar, Python diagnose OK, geen geluid verwacht in US-021."],
  ["US-022", "Story", "Future MIDI En DAW Integratie", "USB MIDI Hardware Input", "Done", "Must", "Lead Developer", 5, "Future", "Generieke USB MIDI inputdiagnose werkt na list-devices en expliciete device/default keuze.", "Hardware MIDI test faalt wanneer Python geen devices scant terwijl Logic devices toont.", "Backenddetails, BLOCKER output en tests/test_hardware_midi.py voor echte device scan.", "US-019, US-024", "Klanttest geslaagd op KodeklopperM4: MIDI input/output devices gelist, inclusief Scarlett 8i6 USB, SMK-37 Pro_BLE en SN76489 CircuitPython ESP32 S2."],
  ["US-023", "Story", "Future MIDI En DAW Integratie", "Studio MIDI Routing Integratietest", "Done", "Should", "QA Engineer", 3, "Future", "Testmatrix dekt DAW bus, USB MIDI, controllers, guitar MIDI, synth hardware, CircuitPython/ESP32, Windows en Raspberry Pi.", "Integratietestplan ontbreekt.", "Routing matrix, host snapshots en placeholder-regel voor device-namen.", "US-022", "docs/studio_midi_routing_integration_v0.1.0.md legt KodeklopperM4 en MuziekM4 snapshots vast als testdata, niet als code constants."],
  ["US-024", "Story", "Future MIDI En DAW Integratie", "MIDI Naar NoteEvent Mapping", "Done", "Must", "DSP Engineer", 5, "Future", "MIDI note on/off wordt correct naar NoteEvent gemapt, inclusief channel en genormaliseerde velocity.", "Mapper tests falen voor note number, channel, velocity, velocity-zero note-off en ontbrekende note-off.", "MidiToNoteEventMapper class en VirtualMidiInputAdapter hergebruik van dezelfde mapper.", "US-006, US-019", "pytest groen: note number 60 -> C4, channels blijven gescheiden, default duration werkt en docs/traceability zijn bijgewerkt."],
  ["US-025", "Story", "Future MIDI En DAW Integratie", "MIDI Device Discovery En Default Selection", "Done", "Must", "Lead Developer", 3, "Future", "CLI scant MIDI devices veilig en kiest input via CLI naam, CLI identifier of YAML default.", "Device discovery, identifier selectie, config precedence en missing-device tests falen.", "MidiDeviceSelector, MidiDeviceSelection en midi list-devices flags --midi-device, --midi-device-id en --config.", "US-019, US-020, US-022", "pytest groen: CLI wint van YAML, output devices worden niet als input geselecteerd, geen hardcoded MIDI device names."],
  ["US-026", "Story", "Future MIDI En DAW Integratie", "Live MIDI Input Receive Loop", "Done", "Must", "Lead Developer", 5, "Future", "CLI luistert bounded naar gekozen MIDI input en mapped note messages naar NoteSequence.", "Normalizer, fake receive backend en midi listen CLI tests falen.", "MidiMessageNormalizer, LiveMidiInputReceiver, MidiInputReceiveSettings/Result en midi listen command.", "US-024, US-025", "pytest groen en hardwaretest geslaagd op KodeklopperM4: SMK-37 Pro_BLE Bluetooth via naamfragment en input:7 ontving echte MIDI note messages."],
  ["US-027", "Story", "Future MIDI En DAW Integratie", "Virtual MIDI Port Voor Logic/DAW", "Done", "Should", "Lead Developer", 5, "Future", "python-d1-synth kan bounded als virtual MIDI destination zichtbaar worden voor Logic/DAW.", "Logic Pro 12.3 moet python-d1-synth tonen als External MIDI destination.", "VirtualMidiPortManager, MidoVirtualMidiPortBackend en midi virtual-port command met fake-backend tests.", "US-026", "Klanttest geslaagd op 2026-07-10 19:25: python-d1-synth zichtbaar als External MIDI destination; niet als Software Instrument is verwacht en buiten US-027."],
  ["US-028", "Story", "Future MIDI En DAW Integratie", "External MIDI Audio Trigger Integratie", "Done", "Must", "DSP Engineer", 8, "Future", "Ontvangen MIDI note events triggeren hoorbaar audio via de bestaande synth engine.", "MidiAudioTrigger en midi play-live tests falen totdat fake MIDI naar fake audio werkt.", "MidiAudioTriggerSettings/Result, MidiAudioTrigger en midi play-live command met fake MIDI en fake audio tests.", "US-026, US-027", "Klanttest geslaagd op KodeklopperM4: SMK-37 Pro_BLE Bluetooth speelde hoorbaar stereo audio via Scarlett 8i6 USB; Logic observatie buiten US-028."],
  ["US-029", "Story", "Future MIDI En DAW Integratie", "Logic/DAW Virtual MIDI Naar Audio Trigger", "Done", "Must", "DSP Engineer", 8, "Future", "Logic/DAW stuurt MIDI naar virtual port en python-d1-synth speelt hoorbare audio.", "Virtual MIDI audio trigger en CLI play-virtual tests falen totdat fake virtual MIDI naar fake audio werkt.", "MidoVirtualMidiInputBackend, VirtualMidiAudioTriggerSettings/Result, VirtualMidiAudioTrigger en midi play-virtual command.", "US-027, US-028", "Klanttest geslaagd: Logic MIDI region speelde hoorbaar geluid; Python ontving note_on:60 velocity=50 channel=1 via python-d1-synth."],
  ["US-030", "Story", "Future MIDI En DAW Integratie", "Logic MIDI Region Multi-Note Playback", "Done", "Must", "DSP Engineer", 5, "Future", "Korte Logic MIDI region met meerdere noten rendert als hoorbare batch.", "Multi-note mapping, fallback timing en verbose sequence-output tests falen.", "MidiMessageNormalizer fallback time, VirtualMidiAudioTriggerResult.played_events en CLI Rendered sequence events output.", "US-029", "Klanttest geslaagd: Logic speelde 5 hoorbare MIDI-triggered note events; circa 2s delay is batch-scope en geen blocker."],
  ["US-031", "Story", "Future MIDI En DAW Integratie", "Live/Streaming MIDI Playback Loop", "Done", "Must", "DSP Engineer", 8, "Future", "Ontvangen note_on events spelen direct als korte audio buffers.", "Streaming backend, per-note audio calls en play-stream CLI tests falen.", "MidoStreamingVirtualMidiInputBackend, StreamingMidiAudioTrigger en midi play-stream command.", "US-030", "Klanttest geslaagd: Logic streamde 18 hoorbare note events; dubbele events worden US-032."],
  ["US-032", "Story", "Future MIDI En DAW Integratie", "Duplicate MIDI Event Guard", "Done", "Must", "DSP Engineer", 5, "Future", "Dubbele MIDI note events uit Logic/routing spelen niet dubbel hoorbaar af, zonder simultane verschillende noten te onderdrukken.", "Dedup window, streaming duplicate suppression, CLI diagnostics en traceability tests falen.", "DuplicateMidiEventGuard, --dedupe-window, suppressed_duplicate_count en docs/duplicate_midi_event_guard_v0.1.0.md.", "US-031", "Klanttest geslaagd: Logic/live playback hoorbaar; 6 note events gespeeld en 23 duplicate MIDI messages onderdrukt. Kleine latency blijft latere story."],
  ["US-033", "Story", "Future MIDI En DAW Integratie", "Note Off Gated Voice Duration", "Done", "Must", "DSP Engineer", 8, "Future", "Note-off bepaalt nootlengte in gated streaming mode in plaats van alleen fixed note-duration.", "Voice mode, note_on/note_off duration, fallback duration, CLI diagnostics en traceability tests falen.", "StreamingVoiceMode, --voice-mode gated, active note state per MIDI key en Streamed note durations output.", "US-032", "Product Owner accepteerde pulse + duration-reporting als tussenstap naar sustained playback."],
  ["US-034", "Story", "Future MIDI En DAW Integratie", "Polyphonic Voice Mixer En Triads", "Done", "Must", "DSP Engineer", 8, "Future", "Drie of meer gelijktijdige noten kunnen als triads hoorbaar worden gemixt.", "Polyphonic mixer tests falen.", "PolyphonicVoiceMixer, chord-window batching en triad playback docs/tests.", "US-033", "Klanttest geslaagd met hoorbare triads; echte sustained audio blijft US-035."],
  ["US-035", "Story", "Future MIDI En DAW Integratie", "Sustained Note Audio Engine", "Done", "Must", "DSP Engineer", 8, "Future", "note_on start een streaming voice en note_off stopt die voice.", "Sustained audio callback en lifecycle tests falen.", "SoundDeviceSustainedAudioPlayer, --voice-mode sustained en held-note diagnostics.", "US-034", "Klanttest geslaagd: sustained mode speelde hoorbaar door tot note-off; Total streamed audio frames: 575172."],
  ["US-036", "Story", "Future MIDI En DAW Integratie", "MIDI Pitch Bend Mapping En DSP", "Done", "Should", "DSP Engineer", 5, "Future", "Pitch bend events buigen sustained oscillatorfrequentie hoorbaar.", "Pitch bend mapping, channel routing en control-message burst tests falen.", "MidiPitchBendMapper, --pitch-bend-range, --pitch-bend-channel-mode en --max-control-messages.", "US-035", "Product Owner accepteerde hoorbare sustained playback, triads, korte/lange nootduur en nette Ctrl-C interrupt met --timeout 600."],
  ["US-037", "Story", "Future MIDI En DAW Integratie", "MIDI Modulation CC1 Mapping En DSP", "Done", "Should", "DSP Engineer", 5, "Future", "CC1 modulation stuurt eenvoudige vibrato-depth op sustained voices aan.", "CC1 normalisatie, modulation mapper, sustained player modulation en CLI diagnostics tests falen.", "MidiModulationMapper, control_change normalisatie, --modulation-vibrato-depth en --modulation-vibrato-rate.", "US-036", "Klanttest geslaagd: pitch bend en CC1 modulation hoorbaar; interrupt-fix getest en akkoord."],
  ["US-038", "Story", "Future MIDI En DAW Integratie", "Performance Mode Until Interrupt", "Done", "Must", "DSP Engineer", 3, "Future", "play-stream kan als performance-run draaien tot Ctrl-C zonder korte testlimiet.", "--until-interrupt, effective backend limits, Ctrl-C cleanup en CLI diagnostics tests falen.", "StreamingMidiAudioTriggerSettings.run_until_interrupted, --until-interrupt en performance-mode README/docs.", "US-037", "Klanttest geslaagd: performance mode met --until-interrupt werkt."],
  ["US-039", "Story", "Future MIDI En DAW Integratie", "Sustain Pedal CC64", "Done", "Must", "DSP Engineer", 5, "Future", "CC64 sustain pedal houdt released sustained voices vast tot pedal up.", "CC64 down/up, held note release, CLI diagnostics en docs tests falen.", "control_change:64 handling in sustained mode, pedal threshold 64 en docs/sustain_pedal_cc64_v0.1.0.md.", "US-035, US-038", "PO accepteerde zonder fysieke sustain pedal, op basis van aanname plus groene automatische CC64-tests."],
  ["US-040", "Story", "Future MIDI En DAW Integratie", "Envelope Release / Soft Note-Off", "Done", "Should", "DSP Engineer", 5, "Future", "note-off en sustain pedal release stoppen met korte fade-out in plaats van hard afkappen.", "release-time, sustained audio envelope, CLI diagnostics en docs tests falen.", "SustainedVoiceState release frames, --release-time en soft note-off docs/tests.", "US-035, US-039", "PO accepteerde US-040 op 2026-07-12; default release_time=0.03s en --release-time 0 zet hard stop terug."],
  ["US-041", "Story", "Future MIDI En DAW Integratie", "Amp Envelope ADSR Parameters", "In Review", "Should", "DSP Engineer", 5, "Future", "Attack, decay, sustain en release vormen de amplitude van sustained voices.", "ADSR settings validation, audio callback envelope, CLI diagnostics en docs tests falen.", "SustainedAudioPlayerSettings ADSR velden, --attack-time, --decay-time, --sustain-level en docs/amp_envelope_adsr_parameters_v0.1.0.md.", "US-040", "In review: commandline ADSR parameters, geen filter envelope, GUI of plugin scope."],
];

board.showGridLines = false;
board.getRange("A1:N1").merge();
board.getRange("A1").values = [["python-d1-synth Sprint 1 Kanban Backlog"]];
board.getRange("A2:N2").merge();
board.getRange("A2").values = [["ChatOD: CHATOD-20260709-D1PY-MVP-001 | Date: 2026-07-09 | Status: Draft for customer review"]];
board.getRange("A4:N4").values = [headers];
board.getRange("A5:N22").values = stories;
const table = board.tables.add("A4:N22", true, "Sprint1Backlog");
table.style = "TableStyleMedium2";
table.showFilterButton = true;

board.getRange("A1:N1").format = {
  fill: "#1F4E79",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center",
};
board.getRange("A2:N2").format = {
  fill: "#D9EAF7",
  font: { italic: true, color: "#1F2937" },
};
board.getRange("A4:N4").format = {
  fill: "#2F75B5",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
};
board.getRange("A5:N22").format = {
  wrapText: true,
  verticalAlignment: "top",
};
board.getRange("H5:H22").setNumberFormat("0");
board.getRange("A4:N22").format.borders = { preset: "inside", style: "thin", color: "#D9E2F3" };
board.getRange("A4:N22").format.autofitColumns();
board.getRange("A4:N22").format.autofitRows();
board.freezePanes.freezeRows(4);
board.getRange("A:A").format.columnWidth = 10;
board.getRange("B:B").format.columnWidth = 10;
board.getRange("C:C").format.columnWidth = 24;
board.getRange("D:D").format.columnWidth = 30;
board.getRange("E:E").format.columnWidth = 14;
board.getRange("F:F").format.columnWidth = 12;
board.getRange("G:G").format.columnWidth = 18;
board.getRange("H:H").format.columnWidth = 12;
board.getRange("I:I").format.columnWidth = 12;
board.getRange("J:N").format.columnWidth = 34;

board.getRange("E5:E100").dataValidation = { rule: { type: "list", values: ["To Do", "In Progress", "In Review", "Done", "Blocked"] } };
board.getRange("F5:F100").dataValidation = { rule: { type: "list", values: ["Must", "Should", "Could", "Won't"] } };
board.getRange("G5:G100").dataValidation = { rule: { type: "list", values: ["Product Owner", "Lead Developer", "DSP Engineer", "QA Engineer", "Release Engineer", "Technical Writer"] } };

future.showGridLines = false;
future.getRange("A1:N1").merge();
future.getRange("A1").values = [["python-d1-synth Future MIDI/DAW Backlog"]];
future.getRange("A2:N2").merge();
future.getRange("A2").values = [["Scope mutation: Logic Pro 12.3, other DAWs, generic USB MIDI, external MIDI, RaspiMidiHub, physical MIDI hub, MiniFreak, Arturia KeyLab Mk3, Fishman TriplePlay, M-Vave"]];
future.getRange("A4:N4").values = [headers];
future.getRange("A5:N27").values = futureStories;
const futureTable = future.tables.add("A4:N27", true, "FutureMidiDawBacklog");
futureTable.style = "TableStyleMedium4";
futureTable.showFilterButton = true;
future.getRange("A1:N1").format = {
  fill: "#385723",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center",
};
future.getRange("A2:N2").format = {
  fill: "#E2F0D9",
  font: { italic: true, color: "#1F2937" },
  wrapText: true,
};
future.getRange("A4:N4").format = {
  fill: "#548235",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
};
future.getRange("A5:N27").format = {
  wrapText: true,
  verticalAlignment: "top",
};
future.getRange("H5:H27").setNumberFormat("0");
future.getRange("A4:N27").format.borders = { preset: "inside", style: "thin", color: "#D9EAD3" };
future.getRange("A4:N27").format.autofitColumns();
future.getRange("A4:N27").format.autofitRows();
future.freezePanes.freezeRows(4);
future.getRange("A:A").format.columnWidth = 10;
future.getRange("B:B").format.columnWidth = 10;
future.getRange("C:C").format.columnWidth = 28;
future.getRange("D:D").format.columnWidth = 34;
future.getRange("E:E").format.columnWidth = 14;
future.getRange("F:F").format.columnWidth = 12;
future.getRange("G:G").format.columnWidth = 18;
future.getRange("H:H").format.columnWidth = 12;
future.getRange("I:I").format.columnWidth = 12;
future.getRange("J:N").format.columnWidth = 36;
future.getRange("E5:E100").dataValidation = { rule: { type: "list", values: ["To Do", "In Progress", "In Review", "Done", "Blocked"] } };
future.getRange("F5:F100").dataValidation = { rule: { type: "list", values: ["Must", "Should", "Could", "Won't"] } };
future.getRange("G5:G100").dataValidation = { rule: { type: "list", values: ["Product Owner", "Lead Developer", "DSP Engineer", "QA Engineer", "Release Engineer", "Technical Writer"] } };

summary.showGridLines = false;
summary.getRange("A1:F1").merge();
summary.getRange("A1").values = [["python-d1-synth Sprint 1 Summary"]];
summary.getRange("A3:B11").values = [
  ["Metric", "Value"],
  ["Total Stories", null],
  ["Must Stories", null],
  ["Should Stories", null],
  ["Total Story Points", null],
  ["In Review", null],
  ["Future MIDI/DAW Stories", null],
  ["Future MIDI/DAW Points", null],
  ["Primary DAW", "Logic Pro 12.3"],
];
summary.getRange("B4:B9").formulas = [
  ["=COUNTA('Sprint 1 Board'!A5:A22)"],
  ["=COUNTIF('Sprint 1 Board'!F5:F22,\"Must\")"],
  ["=COUNTIF('Sprint 1 Board'!F5:F22,\"Should\")"],
  ["=SUM('Sprint 1 Board'!H5:H22)"],
  ["=COUNTIF('Sprint 1 Board'!E5:E22,\"In Review\")"],
  ["=COUNTA('Future MIDI DAW'!A5:A27)"],
];
summary.getRange("B10").formulas = [["=SUM('Future MIDI DAW'!H5:H27)"]];
summary.getRange("D3:F8").values = [
  ["Status", "Count", "Story Points"],
  ["To Do", null, null],
  ["In Progress", null, null],
  ["In Review", null, null],
  ["Done", null, null],
  ["Blocked", null, null],
];
summary.getRange("E4:E8").formulas = [
  ["=COUNTIF('Sprint 1 Board'!E5:E22,D4)"],
  ["=COUNTIF('Sprint 1 Board'!E5:E22,D5)"],
  ["=COUNTIF('Sprint 1 Board'!E5:E22,D6)"],
  ["=COUNTIF('Sprint 1 Board'!E5:E22,D7)"],
  ["=COUNTIF('Sprint 1 Board'!E5:E22,D8)"],
];
summary.getRange("F4:F8").formulas = [
  ["=SUMIF('Sprint 1 Board'!E5:E22,D4,'Sprint 1 Board'!H5:H22)"],
  ["=SUMIF('Sprint 1 Board'!E5:E22,D5,'Sprint 1 Board'!H5:H22)"],
  ["=SUMIF('Sprint 1 Board'!E5:E22,D6,'Sprint 1 Board'!H5:H22)"],
  ["=SUMIF('Sprint 1 Board'!E5:E22,D7,'Sprint 1 Board'!H5:H22)"],
  ["=SUMIF('Sprint 1 Board'!E5:E22,D8,'Sprint 1 Board'!H5:H22)"],
];
summary.getRange("A1:F1").format = {
  fill: "#1F4E79",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center",
};
summary.getRange("A3:B3").format = { fill: "#2F75B5", font: { bold: true, color: "#FFFFFF" } };
summary.getRange("D3:F3").format = { fill: "#2F75B5", font: { bold: true, color: "#FFFFFF" } };
summary.getRange("A3:B11").format.borders = { preset: "all", style: "thin", color: "#D9E2F3" };
summary.getRange("D3:F8").format.borders = { preset: "all", style: "thin", color: "#D9E2F3" };
summary.getRange("A:F").format.autofitColumns();

ref.showGridLines = false;
ref.getRange("A1:D1").merge();
ref.getRange("A1").values = [["Reference Lists"]];
ref.getRange("A3:D3").values = [["Status", "Priority", "Owner", "Debuglevel"]];
ref.getRange("A4:A8").values = [["To Do"], ["In Progress"], ["In Review"], ["Done"], ["Blocked"]];
ref.getRange("B4:B7").values = [["Must"], ["Should"], ["Could"], ["Won't"]];
ref.getRange("C4:C9").values = [["Product Owner"], ["Lead Developer"], ["DSP Engineer"], ["QA Engineer"], ["Release Engineer"], ["Technical Writer"]];
ref.getRange("D4:D6").values = [["none"], ["light"], ["verbose"]];
ref.getRange("A1:D1").format = {
  fill: "#1F4E79",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center",
};
ref.getRange("A3:D3").format = { fill: "#2F75B5", font: { bold: true, color: "#FFFFFF" } };
ref.getRange("A3:D9").format.borders = { preset: "all", style: "thin", color: "#D9E2F3" };
ref.getRange("A:D").format.autofitColumns();

const boardPreview = await workbook.render({
  sheetName: "Sprint 1 Board",
  range: "A1:N23",
  scale: 1,
  format: "png",
});
await fs.writeFile(`${outputDir}/sprint_1_kanban_board_preview.png`, new Uint8Array(await boardPreview.arrayBuffer()));

const summaryPreview = await workbook.render({
  sheetName: "Summary",
  range: "A1:F11",
  scale: 1,
  format: "png",
});
await fs.writeFile(`${outputDir}/sprint_1_summary_preview.png`, new Uint8Array(await summaryPreview.arrayBuffer()));

const futurePreview = await workbook.render({
  sheetName: "Future MIDI DAW",
  range: "A1:N27",
  scale: 1,
  format: "png",
});
await fs.writeFile(`${outputDir}/future_midi_daw_backlog_preview.png`, new Uint8Array(await futurePreview.arrayBuffer()));

const inspect = await workbook.inspect({
  kind: "table",
  range: "'Sprint 1 Board'!A4:N22",
  include: "values,formulas",
  tableMaxRows: 25,
  tableMaxCols: 14,
  maxChars: 6000,
});
console.log(inspect.ndjson);

const futureInspect = await workbook.inspect({
  kind: "table",
  range: "'Future MIDI DAW'!A4:N27",
  include: "values,formulas",
  tableMaxRows: 24,
  tableMaxCols: 14,
  maxChars: 7000,
});
console.log(futureInspect.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${outputDir}/python_d1_synth_sprint_1_kanban_backlog.xlsx`);
