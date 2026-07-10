# USB MIDI Hardware Input

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-022-USB-MIDI-001  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Datum: 2026-07-09  
User Story: US-022 USB MIDI Hardware Input  
Epic: EPIC-007 Future MIDI En DAW Integratie  
Status: In Review, wacht op handmatige hardwaretest

## Doel

US-022 maakt USB MIDI hardware input generiek. De synth mag later niet alleen met een Arturia KeyLab Mk3 werken, maar ook met andere class-compliant of vendor MIDI-bronnen zoals Fishman TriplePlay, M-Vave, RaspiMidiHub routes, MiniFreak MIDI en andere USB MIDI interfaces.

Deze story levert een veilige readiness-diagnose. Live note receive en hoorbare audio-triggering blijven buiten deze stap totdat een hardware device veilig zichtbaar is.

## Wat Nu Werkt

- `UsbMidiHardwareInputAdapter` accepteert elk zichtbaar MIDI input device.
- Device selectie kan op identifier of gedeeltelijke naam, bijvoorbeeld `Fishman`, `M-Vave` of `KeyLab`.
- De testprocedure begint altijd met `list-devices` voordat een specifiek device wordt gekozen.
- Je kunt een device per test kiezen met `--midi-device`, of een default device in de testnotities aanwijzen.
- Output-only devices worden niet als input-ready beschouwd.
- De CLI heeft een hardwarediagnose:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi diagnose-usb-input --midi-device "Fishman"
```

## Structurele Testprocedure

Gebruik deze volgorde voor elke MIDI hardwaretest op `KodeklopperM4` en later ook op `MuziekM4`.

1. Noteer de computernaam: `KodeklopperM4` of `MuziekM4`.
2. Open Audio MIDI Setup en/of Logic Pro en noteer welke MIDI devices zichtbaar zijn.
3. Probeer eerst Python device discovery:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi list-devices --unsafe-rtmidi-scan
```

4. Kies daarna een device uit de lijst, of wijs een default device aan voor deze test.
5. Draai de diagnose met de gekozen naam:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi diagnose-usb-input --unsafe-rtmidi-scan --midi-device "SMK-37"
```

6. Als `MIDI backend failed while scanning devices` verschijnt: behandel dat niet automatisch als geen MIDI setup. Vergelijk dan met Logic/Audio MIDI Setup.

Diagnostic guidance:

```text
First run: python -m synth midi list-devices --unsafe-rtmidi-scan
If Logic Pro shows devices but Python does not, record the Logic/Audio MIDI Setup device list and choose a visible device for the manual test.
```

Voorbeeld van Logic-zichtbare devices op `KodeklopperM4`: `IAC-besturingsbestand`, `Scarlett 8i6 USB`, `Ampero Mini`, `Haxophone`, `Poort 1`, `Poort 2`, `Poort 3`, `SMK-37 Pro_BLE`, `SN76489 Synth Pappavis`, `Software Synthesizer`, `Logic Pro Virtual Out`.

## Testresultaat KodeklopperM4

- CHATOD: CHATOD-20260709-D1PY-MVP-001 / US-022-USB-MIDI-TESTRESULT
- Datum/tijd: 2026-07-10 14:28
- Computernaam: KodeklopperM4
- Gekozen/default device: nog niet gekozen, omdat Python `list-devices` geen device kon tonen.
- Fishman TriplePlay: niet beschikbaar tijdens deze test.
- Logic Pro zichtbare devices: IAC-besturingsbestand, Scarlett 8i6 USB, Ampero Mini, Haxophone, Poort 1, Poort 2, Poort 3, SMK-37 Pro_BLE, SN76489 Synth Pappavis, Software Synthesizer, Logic Pro Virtual Out.
- Command:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi list-devices --unsafe-rtmidi-scan --debuglevel light
```

- CLI output:

```text
MIDI backend failed while scanning devices.
No MIDI devices detected or optional MIDI backend is not installed.
No MIDI devices found.
```

- Beoordeling: US-022 blijft In Review. Logic Pro shows devices but Python does not, dus dit is een Python MIDI backend scan issue en geen bewijs dat de MIDI setup leeg is.

Op macOS blijft native RtMidi/CoreMIDI scanning standaard uitgeschakeld. Als je bewust een echte scan wilt proberen vanuit je eigen Terminal:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi diagnose-usb-input --unsafe-rtmidi-scan
```

## Voorbeelden Van Geldige Input Devices

| Device | Verwachting |
| --- | --- |
| Arturia KeyLab Mk3 | USB MIDI keyboard input met note on/off en velocity. |
| Fishman TriplePlay | MIDI guitar controller input, mogelijk meerdere channels. |
| M-Vave | Generieke USB/BLE MIDI controller of interface, afhankelijk van presentatie in macOS. |
| RaspiMidiHub route | Kan MIDI input doorgeven als macOS input device zichtbaar is. |
| MiniFreak | Kan als MIDI bron dienen wanneer hij als input device zichtbaar is. |

## Handmatige hardwaretest

Voer deze test uit met minstens een van je MIDI USB interfaces en plak het Testresultaat terug in de chat.

```text
CHATOD: CHATOD-20260709-D1PY-MVP-001 / US-022-USB-MIDI-TESTRESULT
Datum/tijd:
macOS versie:
Computernaam: KodeklopperM4/MuziekM4
Logic/Audio MIDI Setup zichtbare devices:
Python list-devices output:
Gekozen/default device:
Getest device:
Device zichtbaar in Audio MIDI Setup: ja/nee
Command:
CLI toont input device: ja/nee
CLI output:
Opmerkingen/screenshot:
```

## Acceptatie

- De story is niet beperkt tot Arturia KeyLab Mk3.
- Fishman TriplePlay, M-Vave en andere USB MIDI interfaces zijn expliciet toegestaan.
- `UsbMidiHardwareInputAdapter` kan een generiek input device selecteren.
- `midi diagnose-usb-input` geeft duidelijke diagnostiek.
- US-022 blijft `In Review` totdat minstens een handmatige hardwaretest is ontvangen.
