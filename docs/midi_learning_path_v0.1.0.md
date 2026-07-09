# MIDI Leerpad En Terminologie

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-019-LEERPAD-001  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Datum: 2026-07-09  
User Story: US-019 MIDI Leerpad En Terminologie  
Epic: EPIC-007 Future MIDI En DAW Integratie

## Doel

Dit leerpad legt de MIDI-basis vast voordat we de Python synth koppelen aan Logic Pro 12.3, een virtual MIDI route, USB MIDI hardware of studio routing via RaspiMidiHub, een fysieke MIDI routing hub, MiniFreak en Arturia KeyLab Mk3.

De ontwerpkeuze blijft: MIDI wordt later vertaald naar ons bestaande `NoteEvent` en `NoteSequence` model. Daardoor blijft de synth-engine onafhankelijk van het protocol.

## Kernbegrippen

| Term | Betekenis Voor Deze Synth |
| --- | --- |
| note on | MIDI-bericht dat zegt dat een toets start. Later mappen we dit naar een intern `NoteEvent` beginpunt. |
| note off | MIDI-bericht dat zegt dat een toets stopt. Later gebruiken we dit om de duur van een noot te bepalen of een actieve stem te stoppen. |
| note number | MIDI gebruikt nummers voor toonhoogtes. Middle C is vaak note number 60, wat meestal C4 betekent. |
| velocity | Aanslagsterkte van een toets, meestal 0-127. Later schalen we dit naar amplitude of expressie. |
| channel | MIDI-kanaal 1-16. Dit helpt meerdere instrumenten of parts op dezelfde verbinding scheiden. |
| MIDI clock | Timing-pulsen waarmee apparaten tempo kunnen synchroniseren. Dit is later relevant voor sequencers/arpeggiators, niet voor Sprint 1 audio. |
| pitch bend | Continue pitch-beweging via een apart bericht, meestal met hogere resolutie dan velocity. Later kan dit oscillatorfrequentie tijdelijk buigen. |

## Praktische Mapping Naar NoteEvent

| MIDI Input | Interne Interpretatie |
| --- | --- |
| note on met velocity groter dan 0 | Start een toekomstige noot in het interne model. |
| note on met velocity 0 | Behandel als note off, omdat veel MIDI-apparaten dit zo sturen. |
| note off | Beeindig de actieve noot of bereken de duur. |
| note number | Vertaal naar nootnaam en frequentie via dezelfde muzikale basisdata als `NoteParser`. |
| velocity | Normaliseer van `0..127` naar `0.0..1.0` voor `NoteEvent.velocity`. |
| channel | Bewaar later als routing- of filterkeuze, nog niet als Sprint 1 audio-eis. |

## Studio Context

De primaire DAW is Logic Pro 12.3 op macOS. De synth moet later ook bruikbaar blijven met andere DAWs. Relevante routes:

- Logic Pro 12.3 stuurt MIDI naar een virtual MIDI input van de Python synth.
- Arturia KeyLab Mk3 stuurt USB MIDI note on, note off, channel en velocity.
- RaspiMidiHub of fysieke MIDI routing hub kan MIDI-bronnen verdelen.
- MiniFreak kan later als externe synth of MIDI-bron in de testmatrix verschijnen.

## Leerpad Voor Volgende Stories

1. Begrijp note on, note off, note number, velocity en channel.
2. Test veilig device discovery zonder macOS CoreMIDI/RtMidi crashroute standaard te activeren.
3. Bouw een `MidiToNoteEventMapper` die alleen protocoldata omzet naar `NoteEvent`.
4. Verbind daarna pas Logic Pro 12.3, Arturia KeyLab Mk3 of andere hardware.
5. Voeg MIDI clock en pitch bend later toe als aparte stories, omdat ze timing en DSP-gedrag raken.

## Buiten Scope Voor US-019

- Geen realtime MIDI input implementatie.
- Geen Logic Pro configuratiestappen.
- Geen VST3 of Audio Unit plugin.
- Geen hardware smoke test met KeyLab Mk3 of MiniFreak.
- Geen pitch bend DSP-implementatie.

## Acceptatie

- De kernbegrippen note on, note off, note number, velocity, channel, MIDI clock en pitch bend zijn verklaard.
- De relatie met `NoteEvent` is expliciet.
- Logic Pro 12.3 en Arturia KeyLab Mk3 staan genoemd als toekomstige context.
- De gids is traceerbaar via Chatlog ID, sprintnummer, doc versie, epic en user story.
