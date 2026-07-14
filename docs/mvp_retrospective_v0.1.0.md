# CHATOD-20260709-D1PY-MVP-001 / MVP Retrospective

- Sprintnummer: MVP Review
- Doc versie: 0.1.0
- Status: Accepted
- Datum: 2026-07-14
- Scope: US-001 t/m US-042

## Wat Ging Goed

- De story-volgorde bleef uiteindelijk sterk: eerst audio en note models, daarna MIDI, daarna Logic, daarna performance controls.
- De commandline-only scope heeft geholpen om snel technische waarheid te vinden zonder GUI/plugin complexiteit.
- Logic Pro External MIDI bleek genoeg om een bruikbare DAW-workflow te bewijzen.
- YAML performance config maakte de lange live commandline praktisch bruikbaar.
- Tests met fake MIDI/audio backends hielden voortgang mogelijk zonder steeds hardware nodig te hebben.
- Product Owner feedback was snel en concreet: hoorbaar geluid, Logic screenshots en terminal output maakten acceptatie helder.

## Wat Was Moeilijk

- macOS CoreMIDI / RtMidi scanroutes konden crashen of zich anders gedragen in sandbox/context.
- MIDI routing in Logic Pro is conceptueel lastig wanneer je geen MIDI-protocolervaring hebt.
- Sommige stories hadden eerst alleen technisch bewijs, waarna pas later muzikaal natuurlijk gedrag ontstond.
- Duplicate MIDI events uit Logic/routing maakten vroege streaming tests verwarrend.
- Ctrl-C cleanup rond sustained audio vereiste extra aandacht.

## Wat Hebben We Geleerd

- MIDI eerst diagnostisch bewijzen voordat audio of synthgedrag verdacht wordt.
- Device names horen runtime data te zijn, geen code constants.
- YAML defaults plus CLI overrides is een goede balans tussen gebruiksgemak en testbaarheid.
- Aparte stories voor pitch bend, modulation, sustain, release en ADSR voorkomen dat de audio engine te snel onoverzichtelijk wordt.
- Een MVP kan professioneel zijn zonder GUI als de workflow, docs, tests en traceability kloppen.

## Procesverbeteringen Voor Volgende Sprint

- Begin elke nieuwe story met een korte acceptatietest die de Product Owner kan uitvoeren.
- Houd hardwareafhankelijke tests opt-in en documenteer exact welke setup nodig is.
- Maak bij elke nieuwe performance feature direct een YAML voorbeeld en een CLI override voorbeeld.
- Blijf onderscheid maken tussen Logic External MIDI, Software Instrument plugins en echte AU/VST3 packaging.
- Voeg bij user-facing features eerst README/usage updates toe voordat de story als Done wordt gemarkeerd.

## Technische Verbeterpunten

- Een audio latency en buffer-size story plannen.
- Een filter/resonance architecture spike plannen voordat de synth te veel performance controls krijgt.
- Een cross-platform Windows audio/MIDI validation story toevoegen.
- Packaging apart behandelen voor macOS en Windows.
- Plugin feasibility apart behandelen; Python MVP code is niet automatisch een AU/VST3 runtime.

## Stop / Start / Continue

Stop:

- Geen nieuwe hardware- of plugin-side quests starten zonder expliciete story.
- Geen machine-specifieke defaults in README startcommando's zetten.

Start:

- Nieuwe user stories clusteren in productrichtingen: synth character, usability, delivery, plugin, hardware port.
- Voor elke demo-route een YAML-first command opnemen.

Continue:

- Class-based code.
- Geen globale application variables.
- Pytest red/green aanpak.
- Traceable docs, stories en commits.
- Product Owner hardware/Logic acceptatie voor user-facing behavior.

## Retrospective Conclusie

De MVP is geslaagd omdat het project de juiste volgorde vond: klein beginnen, hoorbaar bewijs leveren, daarna pas DAW-performance gedrag uitbreiden. De volgende sprint moet niet alles tegelijk willen zijn. Kies een richting, maak die professioneel, en behoud de discipline die deze MVP werkend maakte.
