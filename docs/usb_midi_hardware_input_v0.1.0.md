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
- Output-only devices worden niet als input-ready beschouwd.
- De CLI heeft een hardwarediagnose:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi diagnose-usb-input --midi-device "Fishman"
```

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
