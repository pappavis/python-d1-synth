# Sprint Lessons Learned En Review

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / LESSONS-LEARNED-001  
Sprintnummer: Sprint 0, Sprint 1, Future MIDI/DAW  
Doc versie: 0.1.0  
Datum: 2026-07-11  
Status: Product Owner proposal accepted  
Betrokken stories: US-001 t/m US-031

## Doel

Dit document vat de geleerde lessen samen uit de afgeronde Sprint 0, Sprint 1 en de lopende Future MIDI/DAW sprint. Het doel is om het vendor-proces scherper te maken voordat we verdergaan met nieuwe synth-, MIDI-, packaging- of plugin-stories.

## Sprint Review Samenvatting

Sprint 0 leverde de eerste agile artefacts, MVP-scope en Kanban-backlog op. Sprint 1 leverde een commandline-first Python synth skeleton met oscillator rendering, WAV-export, realtime audio playback, kanaalkeuze, debuglevels, tests en README-instructies.

De Future MIDI/DAW sprint heeft MIDI-leerpad, device discovery, hardware MIDI input, Logic routing, virtual MIDI port, MIDI-to-NoteEvent mapping en Logic/DAW virtual MIDI naar hoorbare audio opgeleverd. US-029 is geslaagd nadat de diagnose-route bewees dat Logic Pro een MIDI region naar `python-d1-synth` stuurde en Python hoorbaar audio renderde.

## Wat Goed Werkte

- Scope-discipline werkte: GUI, AU, VST3 en Logic Component packaging zijn niet ongemerkt in de commandline-MVP geslopen.
- Class-based implementatie en geen globale applicatiestate hielden de code testbaar.
- Red/green pytest-aanpak werkte goed voor parser, oscillator, audio, MIDI en CLI workflows.
- Traceability met ChatOD, backlog, epic, user story en versie maakte code, docs en chatbesluiten navolgbaar.
- Bounded commands met `--max-messages` en `--timeout` maakten MIDI-tests veiliger dan onbeperkte loops.
- Runtime device discovery voorkwam hardcoded MIDI hardware-namen en houdt macOS, Windows, Raspberry Pi en toekomstige CircuitPython-routes open.
- Fake backends en fake audio players maakten automatische tests mogelijk zonder echte hardware.

## Wat Minder Goed Werkte

- We namen soms aan dat "device zichtbaar in Logic" ook betekende dat MIDI-events Python bereikten. US-029 bewees dat dit apart getest moet worden.
- De eerste US-029 testcommand gebruikte te ruime waarden: `--max-messages 10 --timeout 30`. Daardoor leek de applicatie vast te hangen.
- `Ctrl-C` gedrag was pas na een impediment expliciet getest en verbeterd.
- README-instructies waren eerst niet concreet genoeg over Logic tracktype, MIDI destination, MIDI channel en testnoten.
- macOS CoreMIDI/RtMidi gedrag en Python package-conflicten waren echte blockers; deze hadden vroegere dependencydiagnose verdiend.

## Verbeterpunten Voor Volgende Stories

- MIDI moet altijd eerst diagnostisch bewezen worden: zichtbaar in een DAW is niet genoeg; de CLI moet ontvangen events tonen.
- Elke MIDI story start met een diagnosefase: list devices, select device/port, ontvang event, toon event, pas daarna audio verwachten.
- Elke hardware/DAW story moet een korte testcommand hebben, bij voorkeur `--max-messages 1` of `2` met een lage timeout.
- Elke command die langer dan enkele seconden kan lopen moet een geautomatiseerde `KeyboardInterrupt` test hebben.
- README en story-docs moeten exact aangeven: tracktype, destination, channel, testnoot/region, expected CLI output en expected audio gedrag.
- Bij Logic/DAW-integratie moeten we onderscheid blijven maken tussen External MIDI, Software Instrument, AU, VST3 en standalone app.
- Package sanity-checks voor MIDI backends moeten vóór hardwaretests worden uitgevoerd.
- Tests moeten niet alleen "audio speelde" controleren, maar ook "welke MIDI event is ontvangen".

## Concrete Procesafspraken

- Voor elke nieuwe user story toont Codex eerst een uitvoerplan van maximaal ongeveer 250 woorden.
- Bij codewijzigingen blijven headers en docstrings traceerbaar naar ChatOD, sprint, user story, actie en versie.
- Kanban XLSX en Markdown docs blijven samen bijgewerkt.
- Hardwaretests pauzeren voor Product Owner feedback; story status blijft `In Review` tot de handmatige test bevestigd is.
- Als een test faalt, wordt dat als impediment binnen dezelfde story behandeld zolang het dezelfde acceptatiecriteria raakt.
- Nieuwe side quests worden expliciet benoemd en niet geïmplementeerd zonder Product Owner akkoord.

## US-029 Review

US-029 had twee impediments:

- US-029-IMPEDIMENT-001: testinstructies en Ctrl-C gedrag waren onvoldoende duidelijk.
- US-029-IMPEDIMENT-002: Logic zag `python-d1-synth`, maar we moesten eerst bewijzen of MIDI-events Python bereikten.

De uiteindelijke test was geslaagd:

```text
Played 1 MIDI-triggered note events from virtual MIDI port python-d1-synth.
Received MIDI messages: note_on:60:velocity=50:channel=1
Audio buffer: 44100 frames, 44100 Hz
```

Product Owner bevestigde dat er hoorbaar geluid werd afgespeeld door de MIDI region track in Logic. Daardoor is US-029 `Done`.

Statuslabel: US-029 `Done`.

## US-030 Review Voorbereiding

US-030 past direct de US-029 les toe: niet alleen "er is audio" meten, maar ook tonen welke MIDI messages zijn ontvangen en welke sequence events daadwerkelijk zijn gerenderd. Daarom moet de multi-note Logic test altijd met `--debuglevel verbose` draaien en de output `Received MIDI messages` plus `Rendered sequence events` bevatten.

Product Owner bevestigde dat de Logic MIDI region meerdere hoorbare noten afspeelde. De waargenomen vertraging van ongeveer 2 seconden is geen defect binnen US-030, omdat de story bewust batch playback test. Realtime latency wordt apart behandeld in US-031.

Statuslabel: US-030 `Done`.

## US-031 Review Voorbereiding

US-031 volgt direct uit de US-030 observatie dat batch playback hoorbaar werkt maar vertraagd aanvoelt. De review moet daarom niet alleen "maakt geluid" toetsen, maar specifiek vergelijken of `midi play-stream` merkbaar sneller reageert dan `midi play-virtual`.

Statuslabel: US-031 `In Review`.

## Aanbevolen Volgende Stap

De eerstvolgende taak mag pas gekozen worden nadat de Product Owner bevestigt of we:

- US-029 afronding publiceren en daarna de volgende backlog story plannen, of
- eerst de Lessons Learned afspraken in een kleine governance/story-template aanscherpen.
