# Sprint Lessons Learned En Review

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / LESSONS-LEARNED-001  
Sprintnummer: Sprint 0, Sprint 1, Future MIDI/DAW  
Doc versie: 0.1.0  
Datum: 2026-07-11  
Status: Product Owner proposal accepted  
Betrokken stories: US-001 t/m US-034

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

US-031 volgt direct uit de US-030 observatie dat batch playback hoorbaar werkt maar vertraagd aanvoelt. De review bevestigde dat `midi play-stream` realtime hoorbaar werkt. De test bracht een nieuwe, logische vervolgstap naar boven: dubbele MIDI events moeten worden gefilterd of gediagnosticeerd voordat voice-lifecycle, polyfonie, pitch bend en modulation betrouwbaar worden.

Statuslabel: US-031 `Done`.

## US-032 Review Voorbereiding

US-032 behandelt de dubbele Logic/CoreMIDI echo-events uit de US-031 klanttest. De belangrijkste les is dat duplicate filtering de inputstream moet saneren zonder toekomstige muzikale informatie te verliezen: identieke messages binnen een korte window mogen worden onderdrukt, maar verschillende note numbers op dezelfde timestamp moeten blijven bestaan voor latere polyfonie en triads.

De story is bewust beperkt tot streaming duplicate suppression en diagnostics. Note-off gated duration, sustain, polyfonie, pitch bend en modulation blijven aparte user stories.

Product Owner bevestigde de hardware/Logic test als geslaagd: Logic en live note playback waren hoorbaar, met `Streamed 6 MIDI-triggered note events` en `suppressed 23 duplicate MIDI messages`. De kleine resterende vertraging is vastgelegd als latere latency/voice-lifecycle verbetering en geen blocker voor US-032.

Statuslabel: US-032 `Done`.

## US-033 Review Voorbereiding

US-033 volgt bewust na duplicate filtering: pas nadat de inputstream niet meer dubbel speelt, kan note-on/note-off duurmeting betrouwbaar worden getest. De story voegt `--voice-mode gated` toe naast de bestaande fixed mode, zodat US-031/US-032 niet breken terwijl de volgende stap richting echte voice-lifecycle wordt gezet.

Belangrijke scopegrens: deze story meet nootduur, maar implementeert nog geen sustain pedal, envelope release, polyfonie mixer, pitch bend of modulation.

Product Owner bevestigde de test als geslaagd: hoorbaar geluid werd afgespeeld, en bij een 2 seconden vastgehouden noot was duidelijk dat US-033 bewust nog een pulse + duration-reporting tussenstap is. Echte held/sustained audio blijft een latere story.

Statuslabel: US-033 `Done`.

## US-034 Review Voorbereiding

US-034 volgt direct uit US-032 en US-033: duplicate filtering moet chord tones behouden, en note-on events die tegelijk binnenkomen moeten als akkoord kunnen klinken. De story introduceert `PolyphonicVoiceMixer`, streaming MIDI poll-batches en `--chord-window`, zodat triads zoals C-E-G als één chord buffer kunnen worden gemixt.

Belangrijke scopegrens: US-034 mixt polyphonic fixed/fallback buffers, maar implementeert nog geen echte held/sustained audio tussen note-on en note-off, geen pitch bend en geen modulation.

Statuslabel: US-034 `In Review`.

## Aanbevolen Volgende Stap

De eerstvolgende taak mag pas gekozen worden nadat de Product Owner bevestigt of we:

- US-034 accepteren na Logic/keyboard triad-test, of
- een US-034 impediment oplossen als triads nog niet als akkoordbuffer hoorbaar zijn.
