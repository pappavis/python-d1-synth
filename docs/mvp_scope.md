# python-d1-synth MVP Scope

ChatOD: CHATOD-20260709-D1PY-MVP-001 / ARTEFACTS-001
Datum: 2026-07-09
Status: Draft for customer review

## Productvisie

`python-d1-synth` is een Python-first software synthesizer project, geinspireerd door de workflow van klassieke monosynths zoals de Behringer D1. De eerste MVP is geen GUI en geen plugin, maar een commandline-only technische demo waarmee de basis van synthese, audio-output, WAV-rendering en testbare architectuur wordt bewezen.

Het product wordt ontwikkeld alsof een kleine software/synth vendor het project uitvoert voor een klant met MVP-budget. De aanpak is Agile/SCRUM-achtig met user stories, acceptatiecriteria, Kanban backlog en commit checkpoints per afgeronde agile actie.

## Sprint 1 MVP Doel

Sprint 1 bewijst dat de synth via Python 3.11 op macOS hoorbaar geluid kan produceren, WAV-bestanden kan renderen en via commandline bedienbaar is. De focus ligt op technische juistheid, testbaarheid en uitbreidbaarheid. Muzikale verfijning, GUI, MIDI, VST3, Logic AU en standalone installers blijven buiten Sprint 1.

## In Scope Voor Sprint 1

- Commandline-only MVP.
- Python 3.11 projectstructuur.
- Class based code zonder globale variabelen.
- VS Code debug-startpunt en commandline-startpunt.
- `pytest` testframework met red/green ontwikkelaanpak.
- Note parsing voor noten zoals `C3`, `A4`, en testsequences zoals `ACGD`.
- Eigen `NoteEvent` en `NoteSequence` model als voorbereiding op MIDI.
- Oscillator support in volgorde: `sine`, daarna `saw`, daarna `square`.
- Default sample rate: `44100 Hz`.
- Default nootduur: `1.0` seconde.
- CLI override voor duur, bijvoorbeeld `--duration 2.5`.
- Realtime play command, bijvoorbeeld `python -m synth play --note C3`.
- Dumb user testmode, bijvoorbeeld `python -m synth play --testsequence "ACGD" --debuglevel light`.
- YAML patch-configs.
- WAV render command, bijvoorbeeld `python -m synth render patch.yaml --output demo.wav`.
- Output channel opties: `stereo`, `left`, `right`.
- README-instructies voor starten, testen en debuggen.
- MIT license als default publieke repo-keuze.

## Out Of Scope Voor Sprint 1

- GUI.
- VST3 plugin.
- Logic Audio Unit component.
- Standalone macOS `.app` packaging.
- Standalone Windows executable packaging.
- MIDI input.
- MIDI clock.
- Pitch bend.
- Filter/envelope karakter als volledig muzikaal systeem.
- Preset browser.
- Realtime polyfonie.
- CircuitPython/ESP32 implementatie.
- I2S/PWM audio-output op hardware.

## Later Productspoor

Na goedkeuring van de MVP kan het project in latere sprints doorgroeien naar:

- MIDI input en MIDI protocol begeleiding.
- DAW-integratie met Logic Pro 12.3 op macOS en waar mogelijk andere DAWs.
- Beschikbaar maken als MIDI-bespeelbare synth vanuit een DAW, bijvoorbeeld via een virtual MIDI port, external MIDI workflow of latere plugin-route.
- USB MIDI en external MIDI workflows met bestaande hardware in de studio.
- MIDI device discovery via commandline, zodat beschikbare USB/virtual/external MIDI devices gescand en getoond kunnen worden.
- MIDI device selectie via CLI argument of YAML default-config.
- Testen met de bekende studio-opstelling: RaspiMidiHub, fysieke MIDI routing hub, MiniFreak synth en Arturia KeyLab Mk3 MIDI keyboard.
- ADSR envelope.
- Low-pass filter met cutoff/resonance.
- Meer oscillator mix en D1-achtige workflow.
- GUI.
- VST3/AU strategie via native wrapper of port.
- Standalone macOS/Windows packaging.
- CircuitPython 10 fork voor Lolin Wemos S2 Mini met I2S of PWM audio-output.

## Technische Richting

De beoogde MVP stack is:

- Python 3.11.
- `numpy` voor audiosample generatie.
- `sounddevice` voor realtime audio-output.
- Python `wave` module voor eenvoudige WAV export.
- `pytest` voor tests.
- YAML voor patch-configuratie.

De plugin-route wordt later apart onderzocht. VST3 en Logic AU zijn native plugin ecosystemen; Python is geschikt voor MVP en DSP-prototyping, maar waarschijnlijk niet als directe plugin runtime zonder wrapper of port.

## DAW En MIDI Context

De klant gebruikt Logic Pro 12.3 op macOS als primaire DAW, maar wil het ontwerp niet onnodig beperken tot Logic alleen. De synth moet later vanuit Logic of een andere DAW als MIDI-bespeelbaar instrument bruikbaar worden. Daarbij zijn twee routes relevant:

- Software route: een virtual MIDI port of DAW-external-MIDI workflow waarmee note events vanuit de DAW naar de Python synth kunnen worden gestuurd.
- Plugin route: latere VST3/Logic AU strategie via native wrapper, port of aparte pluginlaag.

De studio bevat daarnaast MIDI-hardware die later in integratietests moet terugkomen:

- RaspiMidiHub.
- Fysieke MIDI routing hub.
- MiniFreak synth.
- Arturia KeyLab Mk3 MIDI keyboard.

Deze MIDI/DAW-integratie is bewust buiten Sprint 1 gehouden, maar wordt als future backlog opgenomen zodat de MVP-architectuur het niet blokkeert.

De toekomstige commandline moet daarnaast MIDI devices kunnen ontdekken en selecteren. Een beoogde vorm is:

- `python -m synth midi list-devices`
- `python -m synth play --midi-device "Arturia KeyLab Mk3"`
- `python -m synth play --midi-device-id "<device-id>"`
- YAML config met bijvoorbeeld `midi.default_input_device`.

De exacte namen en identifiers worden later platformafhankelijk getest, omdat macOS, Windows, virtual MIDI ports en hardware hubs devices verschillend kunnen presenteren.

## Definition Of Done Voor Sprint 1

Sprint 1 is geslaagd wanneer:

- `python -m synth play --note C3` hoorbaar geluid maakt op macOS.
- `python -m synth render patch.yaml --output demo.wav` een bruikbaar WAV-bestand maakt.
- `--channel stereo`, `--channel left` en `--channel right` correct werken.
- Tests groen draaien.
- README uitlegt hoe de MVP gestart, getest en in VS Code gedebugd wordt.
- Alle Sprint 1 user stories hebben acceptatiecriteria.
- De Kanban backlog is bijgewerkt.
