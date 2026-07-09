# External MIDI Workflow In Logic

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-021-LOGIC-WORKFLOW-001  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Datum: 2026-07-09  
User Story: US-021 External MIDI Workflow In Logic  
Epic: EPIC-007 Future MIDI En DAW Integratie  
Status: Done

## Doel

Deze workflow beschrijft hoe Logic Pro 12.3 later MIDI naar `python-d1-synth` kan sturen zonder meteen een VST3 of Audio Unit plugin te bouwen. De route gebruikt een external MIDI workflow via macOS MIDI-routing. Voor de eerste handmatige test gebruiken we bij voorkeur de ingebouwde IAC Driver in Audio MIDI Setup.

US-021 opent nog geen live MIDI-poort in de synth. De code uit US-020 bewijst wel dat MIDI note-on/off berichten naar `NoteSequence` en `NoteEvent` gemapt kunnen worden. Deze workflow controleert nu of de DAW-route reproduceerbaar genoeg is.

## Voorbereiding

1. Open `Audio MIDI Setup` op macOS.
2. Open het MIDI Studio venster.
3. Open `IAC Driver`.
4. Zet `Device is online` aan.
5. Maak of controleer een busnaam, bijvoorbeeld `python-d1-synth`.
6. Start daarna in de projectmap:

```bash
cd /Volumes/data1/Yandex.Disk.localized/michiele/Programmering/Python/python_normaal/github_python_normaal/desktop_synth
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi diagnose-virtual-input
```

Verwacht resultaat:

```text
Virtual MIDI input backend is installed. Route a DAW track to 'python-d1-synth' when the live input story opens the port.
```

## Logic Pro 12.3 Route

1. Open Logic Pro 12.3.
2. Open of maak een leeg project.
3. Maak een `External MIDI` track.
4. Kies als MIDI destination de IAC Driver bus, bijvoorbeeld `python-d1-synth`.
5. Zet MIDI channel op `1` voor de eerste test.
6. Maak een korte regio met een paar noten, bijvoorbeeld C4, E4 en G4.
7. Speel de regio af.
8. Noteer of Logic Pro 12.3 de IAC Driver bus laat kiezen en of playback zonder foutmelding start.

## Wat Deze Test Wel En Niet Bewijst

Wel:

- Logic Pro 12.3 kan een External MIDI track naar een macOS MIDI-route sturen.
- De IAC Driver route kan als tussenstap dienen voor de standalone Python synth.
- De toekomstige live-input story kan deze route gebruiken als bron.

Niet:

- De Python synth ontvangt nog geen live MIDI.
- Er is nog geen audio-plugin.
- Er is nog geen realtime MIDI performance workflow.
- Er is nog geen hardwaretest met Arturia KeyLab Mk3, MiniFreak of RaspiMidiHub.

## Handmatige test

Voer deze test uit en plak het Testresultaat terug in de chat.

```text
CHATOD: CHATOD-20260709-D1PY-MVP-001 / US-021-LOGIC-TESTRESULT
Datum/tijd:
macOS versie:
Logic Pro versie:
IAC Driver online: ja/nee
IAC busnaam:
External MIDI track kon bus kiezen: ja/nee
MIDI channel:
Testnoten:
Playback start zonder Logic foutmelding: ja/nee
Opmerkingen/screenshot:
```

## Testresultaat

- CHATOD: CHATOD-20260709-D1PY-MVP-001 / US-021-LOGIC-TESTRESULT
- Datum/tijd: 2026-07-09 17:45
- Tester: Michiel
- MIDI Studio: IAC-besturingsbestand zichtbaar in Audio MIDI Setup
- Python diagnose: geslaagd
- Logic Pro route: External MIDI op IAC external MIDI channel 1 toegevoegd
- Testactie: note gespeeld vanuit Logic Pro route
- Geluid hoorbaar: nee
- Beoordeling: geslaagd voor US-021

Commandline bewijs:

```text
Virtual MIDI input backend is installed. Route a DAW track to 'python-d1-synth' when the live input story opens the port.
```

Belangrijk: geen geluid is verwacht in US-021. Deze story bewijst alleen dat de Logic/IAC-route en Python MIDI-backenddiagnose reproduceerbaar zijn. Live MIDI ontvangen, note events realtime naar de synth-engine sturen en audio triggeren horen bij de volgende implementatiestory.

## Acceptatie Voor US-021

- De workflow is reproduceerbaar beschreven.
- Logic Pro 12.3, IAC Driver, Audio MIDI Setup, External MIDI en `python-d1-synth` zijn expliciet genoemd.
- De test blijft veilig: geen live CoreMIDI/RtMidi input in Python tijdens deze story.
- Het handmatige Logic/IAC testresultaat is ontvangen en vastgelegd.
