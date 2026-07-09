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
  ["US-006", "Story", "Muzikale Basisdata", "NoteEvent En NoteSequence Model", "In Review", "Must", "DSP Engineer", 3, "Sprint 1", "Intern eventmodel ondersteunt note, duration, velocity en timing.", "Modelvalidatie tests falen.", "Class based event/sequence model.", "US-004", "Dataclasses toegevoegd als basis voor MIDI mapping."],
  ["US-007", "Story", "Oscillator En Audio Rendering", "Sine Oscillator", "Done", "Must", "DSP Engineer", 5, "Sprint 1", "Sine samples hebben juiste lengte en amplitude.", "Sample count/amplitude tests falen.", "SineOscillator class met numpy.", "US-006", "pytest dekt sample count en amplitude."],
  ["US-008", "Story", "Oscillator En Audio Rendering", "Saw Oscillator", "In Review", "Should", "DSP Engineer", 3, "Sprint 1", "Saw samples hebben juiste lengte en amplitude.", "Saw oscillator tests falen.", "SawOscillator class.", "US-007", "Waveform enum en oscillator ondersteunen saw."],
  ["US-009", "Story", "Oscillator En Audio Rendering", "Square Oscillator", "In Review", "Should", "DSP Engineer", 3, "Sprint 1", "Square samples hebben juiste lengte en amplitude.", "Square oscillator tests falen.", "SquareOscillator class.", "US-007", "Waveform enum en oscillator ondersteunen square."],
  ["US-010", "Story", "Oscillator En Audio Rendering", "WAV Export", "Done", "Must", "Lead Developer", 5, "Sprint 1", "Render command schrijft stereo WAV op 44100 Hz.", "WAV bestandsinspectie faalt.", "WaveWriter class met standaard wave module.", "US-007", "CLI render maakte outputs/demo.wav met 2 kanalen, 44100 Hz, 44100 frames."],
  ["US-011", "Story", "Realtime CLI Playback", "Play Single Note", "To Do", "Must", "Lead Developer", 5, "Sprint 1", "play --note C3 maakt hoorbaar geluid.", "Audio output adapter test faalt.", "sounddevice adapter en CLI play command.", "US-007", "Adapter aanwezig; hoorbare output nog niet handmatig geverifieerd."],
  ["US-012", "Story", "Realtime CLI Playback", "Play Testsequence", "To Do", "Must", "Lead Developer", 3, "Sprint 1", "play --testsequence ACGD speelt vier noten.", "Sequence playback test faalt.", "Playback engine voor NoteSequence.", "US-005, US-011", "Dumb user testmode."],
  ["US-013", "Story", "Realtime CLI Playback", "Channel Selection", "In Review", "Must", "QA Engineer", 3, "Sprint 1", "stereo/left/right kanaalrouting werkt.", "Kanaalrouting tests falen.", "ChannelRouter class en CLI option.", "US-010, US-011", "ChannelRouter en test aangemaakt."],
  ["US-014", "Story", "Configuratie En CLI", "YAML Patch Config", "Done", "Must", "Lead Developer", 3, "Sprint 1", "Patch YAML laadt oscillator, duration, sample_rate en channel.", "Patch loader tests falen.", "PatchConfig class en loader.", "US-007", "PyYAML loader, example patch en config test toegevoegd."],
  ["US-015", "Story", "Configuratie En CLI", "Render Command", "Done", "Must", "Lead Developer", 3, "Sprint 1", "render patch.yaml --output demo.wav schrijft WAV.", "CLI render test faalt.", "argparse command en render workflow.", "US-010, US-014", "CLI render succesvol geverifieerd."],
  ["US-016", "Story", "Configuratie En CLI", "Debuglevel", "In Review", "Should", "QA Engineer", 2, "Sprint 1", "none/light/verbose tonen juiste hoeveelheid output.", "CLI output tests falen.", "DebugLevel enum/class en reporter.", "US-011, US-015", "DebugReporter toegevoegd; outputtests nog niet uitgevoerd."],
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
  ["US-019", "Story", "Future MIDI En DAW Integratie", "MIDI Leerpad En Terminologie", "To Do", "Must", "Product Owner", 2, "Future", "Klant begrijpt note on/off, channel, velocity, clock en pitch bend.", "Docs ontbreken voor MIDI basisbegrippen.", "MIDI concept guide en glossary.", "US-006", "Eerst uitleg voordat hardware-integratie start."],
  ["US-020", "Story", "Future MIDI En DAW Integratie", "Virtual MIDI Input Voor DAW", "To Do", "Must", "Lead Developer", 5, "Future", "Logic Pro 12.3 of andere DAW kan note events naar de synth sturen.", "Virtual MIDI route test faalt.", "Virtual MIDI input adapter en event bridge.", "US-006, US-019", "Software route naast latere pluginroute."],
  ["US-021", "Story", "Future MIDI En DAW Integratie", "External MIDI Workflow In Logic", "To Do", "Should", "Release Engineer", 3, "Future", "External MIDI workflow in Logic is reproduceerbaar beschreven.", "Logic external MIDI setup test faalt of ontbreekt.", "Setup guide en handmatige DAW test.", "US-020", "Logic Pro 12.3 is primaire DAW, maar ontwerp blijft DAW-breed."],
  ["US-022", "Story", "Future MIDI En DAW Integratie", "USB MIDI Hardware Input", "To Do", "Must", "Lead Developer", 5, "Future", "Arturia KeyLab Mk3 kan note on/off en velocity aanleveren.", "USB MIDI device detectie test faalt.", "USB MIDI input adapter en hardware smoke test.", "US-019, US-024", "Eerste fysieke controller."],
  ["US-023", "Story", "Future MIDI En DAW Integratie", "Studio MIDI Routing Integratietest", "To Do", "Should", "QA Engineer", 3, "Future", "Testmatrix dekt RaspiMidiHub, fysieke MIDI hub, MiniFreak en KeyLab Mk3.", "Integratietestplan ontbreekt.", "Routing testmatrix en testnotities.", "US-022", "Studio-opstelling expliciet documenteren."],
  ["US-024", "Story", "Future MIDI En DAW Integratie", "MIDI Naar NoteEvent Mapping", "To Do", "Must", "DSP Engineer", 5, "Future", "MIDI note on/off wordt correct naar NoteEvent gemapt.", "Mapper tests falen voor note number, channel en velocity.", "MidiToNoteEventMapper class.", "US-006, US-019", "Houdt Sprint 1 engine herbruikbaar."],
  ["US-025", "Story", "Future MIDI En DAW Integratie", "MIDI Device Discovery En Default Selection", "In Review", "Must", "Lead Developer", 3, "Future", "CLI scant MIDI devices en kiest device via CLI of YAML default.", "Device discovery en config precedence tests falen.", "MidiDeviceScanner, CLI list-devices en config default.", "US-019, US-020, US-022", "Skeleton toegevoegd; optionele mido/backend nog nodig voor echte devices."],
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
future.getRange("A2").values = [["Scope mutation: Logic Pro 12.3, other DAWs, USB MIDI, external MIDI, RaspiMidiHub, physical MIDI hub, MiniFreak, Arturia KeyLab Mk3"]];
future.getRange("A4:N4").values = [headers];
future.getRange("A5:N11").values = futureStories;
const futureTable = future.tables.add("A4:N11", true, "FutureMidiDawBacklog");
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
future.getRange("A5:N11").format = {
  wrapText: true,
  verticalAlignment: "top",
};
future.getRange("H5:H11").setNumberFormat("0");
future.getRange("A4:N11").format.borders = { preset: "inside", style: "thin", color: "#D9EAD3" };
future.getRange("A4:N11").format.autofitColumns();
future.getRange("A4:N11").format.autofitRows();
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
  ["=COUNTA('Future MIDI DAW'!A5:A11)"],
];
summary.getRange("B10").formulas = [["=SUM('Future MIDI DAW'!H5:H11)"]];
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
  range: "A1:N22",
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
  range: "A1:N11",
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
  range: "'Future MIDI DAW'!A4:N11",
  include: "values,formulas",
  tableMaxRows: 12,
  tableMaxCols: 14,
  maxChars: 5000,
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
