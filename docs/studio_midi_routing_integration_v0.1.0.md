# Studio MIDI Routing Integratietest

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-023-STUDIO-MIDI-ROUTING-001  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Datum: 2026-07-10  
User Story: US-023 Studio MIDI Routing Integratietest  
Epic: EPIC-007 Future MIDI En DAW Integratie  
Status: Done, testmatrix en routingprocedure opgesteld

## Doel

US-023 legt een reproduceerbare studio MIDI routing testmatrix vast voor `python-d1-synth`. Deze story implementeert nog geen live MIDI receive of hoorbare MIDI-triggering. Het doel is dat elke computer eerst zijn MIDI devices kan scannen, dat routingpaden als testdata worden vastgelegd, en dat toekomstige stories MIDI events veilig naar `NoteEvent` kunnen mappen.

Belangrijk ontwerpprincipe: device-namen zoals `Scarlett 8i6 USB`, `GM-800`, `MiniFreak MIDI`, `SN76489 Synth Pappavis CircuitPython usb_midi.ports[0]` of `KL Essential 49 mk3 MIDI` zijn omgevings-snapshots. Ze mogen nooit als constants of verplichte namen in applicatiecode worden vastgelegd. De applicatie moet op willekeurige computers kunnen draaien, inclusief macOS hosts, Windows `Spelen01`, Raspberry Pi 2 of een toekomstige CircuitPython/ESP32 route.

## Algemene Testprocedure

Gebruik deze procedure per host en per MIDI route:

1. Noteer hostnaam, OS, Pythonpad en git commit.
2. Scan devices:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi list-devices --unsafe-rtmidi-scan --debuglevel light
```

3. Kopieer de volledige input/output lijst naar het testresultaat.
4. Kies een route op basis van runtime-discovery, niet op basis van hardcoded namen.
5. Noteer gekozen input, gekozen output, routingbron, verwachte rol en teststatus.
6. Als een device niet bestaat op de host, markeer de route als `Not Available`, niet als codefout.
7. Herhaal later op Windows `Spelen01` en Raspberry Pi 2 met platform-specifiek Pythonpad.

## Routing Matrix Template

| Route ID | Host | Source Type | Input Device Selector | Output Device Selector | Verwachte Rol | Status | Opmerking |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RT-001 | any | DAW virtual bus | discovered IAC/virtual input | discovered IAC/virtual output | DAW route voorbereiden | To Test | Gebruik runtime device listing. |
| RT-002 | any | USB audio/MIDI interface | discovered class-compliant MIDI input | discovered class-compliant MIDI output | Externe interface route | To Test | Niet koppelen aan merknaam in code. |
| RT-003 | any | MIDI keyboard/controller | discovered keyboard input | optional output | Note on/off bron | To Test | Later relevant voor US-024. |
| RT-004 | any | Guitar MIDI controller | discovered guitar MIDI input | optional output | Multi-channel note bron | To Test | Let later op channel/velocity. |
| RT-005 | any | Synth hardware | discovered synth input/output | discovered synth output/input | Synth als bron of target | To Test | Kan input, output of beide zijn. |
| RT-006 | any | CircuitPython/ESP32 device | discovered usb_midi input/output | discovered usb_midi output/input | Future embedded port route | To Test | Namen zijn testdata, geen constants. |
| RT-007 | Spelen01 | Windows MIDI stack | discovered Windows MIDI device | discovered Windows MIDI device | Cross-platform check | Planned | Uitvoeren op Windows. |
| RT-008 | Raspberry Pi 2 | Linux ALSA/JACK MIDI | discovered ALSA/JACK device | discovered ALSA/JACK device | Low-resource host check | Planned | Pythonpad en backend later bepalen. |

## KodeklopperM4 Snapshot

Deze snapshot is testdata uit US-022 en mag niet als vaste deviceconfiguratie worden gebruikt.

```text
input:0 input   IAC-besturingsbestand Bus 1
input:1 input   Scarlett 8i6 USB
input:2 input   Ampero Mini
input:3 input   Haxophone
input:4 input     Poort 1
input:5 input     Poort 2
input:6 input     Poort 3
input:7 input   SMK-37 Pro_BLE Bluetooth
input:8 input   SN76489 Synth Pappavis CircuitPython usb_midi.ports[0]
output:0        output  IAC-besturingsbestand Bus 1
output:1        output  Scarlett 8i6 USB
output:2        output  Ampero Mini
output:3        output  Haxophone
output:4        output    Poort 1
output:5        output    Poort 2
output:6        output    Poort 3
output:7        output  SMK-37 Pro_BLE Bluetooth
output:8        output  SN76489 Synth Pappavis CircuitPython usb_midi.ports[0]
output:9        output  Software Synthesizer
```

## MuziekM4 Snapshot

Deze snapshot is testdata uit `Muziekm4_midi_devices_scanned_2026-07-10.txt` en mag niet als vaste deviceconfiguratie worden gebruikt.

```text
input:0 input   GM-800
input:1 input   GM-800 DAW CTRL
input:2 input   GX-100
input:3 input   GX-100 DAW CTRL
input:4 input   USB MIDI-apparaat
input:5 input   BOSS_RC-10R
input:6 input   AMYboard
input:7 input   RC-600
input:8 input   TriplePlay Express Geel strat TP Guitar
input:9 input   TriplePlay Express Geel strat TP Control
input:10        input   MiniFreak MIDI
input:11        input   TriplePlay Express Ovation TP Guitar
input:12        input   TriplePlay Express Ovation TP Control
input:13        input   KL Essential 49 mk3 MIDI
input:14        input   KL Essential 49 mk3 DINTHRU
input:15        input   KL Essential 49 mk3 MCU/HUI
input:16        input   KL Essential 49 mk3 ALV
input:17        input   IAC MIidi poort Bus 1
input:18        input   IAC MIidi poort Bus 2
output:0        output  GM-800
output:1        output  GM-800 DAW CTRL
output:2        output  GX-100
output:3        output  GX-100 DAW CTRL
output:4        output  USB MIDI-apparaat
output:5        output  BOSS_RC-10R
output:6        output  AMYboard
output:7        output  RC-600
output:8        output  TriplePlay Express Geel strat TP Guitar
output:9        output  TriplePlay Express Geel strat TP Control
output:10       output  MiniFreak MIDI
output:11       output  TriplePlay Express Ovation TP Guitar
output:12       output  TriplePlay Express Ovation TP Control
output:13       output  KL Essential 49 mk3 MIDI
output:14       output  KL Essential 49 mk3 DINTHRU
output:15       output  KL Essential 49 mk3 MCU/HUI
output:16       output  KL Essential 49 mk3 ALV
output:17       output  IAC MIidi poort Bus 1
output:18       output  IAC MIidi poort Bus 2
output:19       output  Software Synthesizer
```

## Testresultaat Template

```text
CHATOD: CHATOD-20260709-D1PY-MVP-001 / US-023-STUDIO-MIDI-ROUTING-TESTRESULT
Datum/tijd:
Hostnaam:
OS:
Python:
Git commit:
Device scan command:
Device scan output:
Route ID:
Gekozen input selector:
Gekozen output selector:
Waarom deze route:
Resultaat: Pass/Fail/Not Available
Opmerkingen:
```

## Acceptatie

- Routingmatrix bestaat voor DAW, USB interface, keyboard/controller, guitar MIDI, synth hardware, CircuitPython/ESP32, Windows `Spelen01` en Raspberry Pi 2.
- KodeklopperM4 en MuziekM4 scans zijn vastgelegd als snapshots/testdata.
- Documentatie zegt expliciet dat device-namen placeholders zijn en niet als constants in code mogen worden gebruikt.
- De procedure begint altijd met runtime MIDI device discovery.
- US-023 is `Done` wanneer deze testmatrix en procedure in docs, acceptatiecriteria en Kanban staan.
