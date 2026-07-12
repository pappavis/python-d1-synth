# Sprint Lessons Learned En Review

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / LESSONS-LEARNED-001  
Sprintnummer: Sprint 0, Sprint 1, Future MIDI/DAW  
Doc versie: 0.1.0  
Datum: 2026-07-12
Status: Product Owner proposal accepted  
Betrokken stories: US-001 t/m US-040

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

Product Owner bevestigde de triad/akkoordtest als geslaagd genoeg met `--chord-window 0.08`: er waren hoorbare akkoordachtige groepen, verschillende chord tones bleven behouden en duplicate filtering verwijderde geen muzikale noten.

Statuslabel: US-034 `Done`.

## US-035 Review Voorbereiding

US-035 volgt direct uit de Product Owner observatie dat een 2 seconden vastgehouden C3 in US-033/US-034 nog als kort pulse-nootje klonk. De story introduceert `--voice-mode sustained`, `SoundDeviceSustainedAudioPlayer` en een streaming audiocallback zodat `note_on` een voice start en `note_off` die voice stopt.

Belangrijke scopegrens: US-035 behandelt de note-on/note-off voice lifecycle. Sustain pedal, envelope release, pitch bend, modulation, GUI en plugin packaging blijven aparte stories.

Product Owner bevestigde de sustained playback test als geslaagd: noten bleven hoorbaar tot note-off en de CLI rapporteerde `Total streamed audio frames: 575172`.

Statuslabel: US-035 `Done`.

## US-036 Review Voorbereiding

US-036 volgt logisch na sustained playback, omdat pitch bend alleen zinvol hoorbaar is wanneer een voice actief blijft klinken. De story voegt mido `pitchwheel` normalisatie, `MidiPitchBendMapper`, `--pitch-bend-range` en `SoundDeviceSustainedAudioPlayer.pitch_bend(...)` toe.

Belangrijke scopegrens: US-036 behandelt pitch bend op actieve sustained voices. Sustain pedal, envelope release, GUI en plugin packaging blijven aparte stories.

Impediment-001 les: verbose MIDI logging moet altijd channel-informatie tonen en de acceptatietest moet controleren of `note_on` en `pitch_bend` op hetzelfde channel binnenkomen. De SMK37/Logic test liet `note_on` op channel 1 en pitch bend op channel 4 zien; daarom is `--pitch-bend-channel-mode omni` toegevoegd als expliciete MVP/diagnose-route zonder de veilige default `same` te wijzigen.

Product Owner bevestigde US-036 op 2026-07-12 als geslaagd: er was hoorbaar geluid, triads speelden, korte en lange noten hadden hoorbaar correcte duur, en een langere sessie met `--timeout 600` stopte netjes met `Ctrl-C`.

Statuslabel: US-036 `Done`.

## US-037 Review Voorbereiding

US-037 volgt direct uit US-036: nadat sustained playback en pitch bend werken, kan CC1 modulation als volgende MIDI performance control worden gemapt. De story voegt mido `control_change` normalisatie, `MidiModulationMapper`, `--modulation-vibrato-depth`, `--modulation-vibrato-rate` en `SoundDeviceSustainedAudioPlayer.modulation(...)` toe.

Belangrijke scopegrens: US-037 gebruikt CC1 alleen voor eenvoudige vibrato-depth. Filter-modulatie, sustain pedal, envelope release, GUI en plugin packaging blijven aparte stories.

Product Owner bevestigde US-037 op 2026-07-12 als geslaagd: pitch bend werkt, CC1 modulation is hoorbaar, en de interrupt-fix is getest en akkoord.

Statuslabel: US-037 `Done`.

US-037-IMPEDIMENT-001 les: sustained audio cleanup mag bij `Ctrl-C` niet vertrouwen op een gewone PortAudio/CoreAudio `stop()`, omdat die in lange performance-sessies kan blokkeren. De interrupt-route gebruikt nu `abort()` wanneer beschikbaar en valt alleen terug naar `stop()` als de stream geen abort ondersteunt.

## US-038 Review Voorbereiding

US-038 volgt direct uit de Product Owner vraag om de synth "gewoon te gebruiken" zonder korte testlimieten. De story voegt `--until-interrupt` toe aan `midi play-stream`, zodat de commandline performance-run primair stopt via `Ctrl-C`.

Belangrijke scopegrens: US-038 verandert alleen de sessielimiet van de bestaande streaming route. Sustain pedal, envelope release, GUI en plugin packaging blijven aparte stories.

Product Owner bevestigde US-038 op 2026-07-12 als geslaagd.

Statuslabel: US-038 `Done`.

## US-039 Review Voorbereiding

US-039 volgt logisch na sustained voices, pitch bend, modulation en performance mode: een speler verwacht dat MIDI CC64 sustain pedal een losgelaten toets hoorbaar vasthoudt totdat de pedal omhoog gaat.

Belangrijke scopegrens: US-039 implementeert alleen binaire sustain pedal down/up met CC64 threshold 64. Half-pedal curves, sostenuto, envelope release, GUI en plugin packaging blijven aparte stories.

Product Owner accepteerde US-039 op 2026-07-12 zonder fysieke sustain pedal, op basis van aanname plus groene automatische CC64-tests. Les: wanneer hardware ontbreekt, moet de story duidelijk vastleggen of acceptatie hardwarematig, DAW-matig of op basis van testdekking gebeurt.

Statuslabel: US-039 `Done`.

## US-040 Review Voorbereiding

US-040 volgt direct uit US-035 en US-039: sustained voices stoppen functioneel correct, maar hard note-off en sustain-release kunnen click-achtig of te abrupt klinken. De story voegt daarom een korte release envelope toe via `--release-time`.

Belangrijke scopegrens: US-040 behandelt alleen soft note-off/release fade in sustained mode. Volledige ADSR, filter envelope, velocity-afhankelijke release curves, GUI en plugin packaging blijven aparte stories.

Statuslabel: US-040 `In Review`.

## Aanbevolen Volgende Stap

De eerstvolgende taak na US-040 review is een kleine acceptatie- of afrondingsstap: Product Owner vergelijkt `--release-time 0.03` met `--release-time 0`, waarna US-040 naar `Done` kan of een impediment kan worden vastgelegd.
