# USB MIDI Hardware Input

Chatlog ID: CHATOD-20260709-D1PY-MVP-001 / US-022-USB-MIDI-001  
Sprintnummer: Future MIDI/DAW  
Doc versie: 0.1.0  
Datum: 2026-07-09  
User Story: US-022 USB MIDI Hardware Input  
Epic: EPIC-007 Future MIDI En DAW Integratie  
Status: Blocked, Python MIDI backend scan ziet geen devices terwijl Logic Pro wel devices toont

## Doel

US-022 maakt USB MIDI hardware input generiek. De synth mag later niet alleen met een Arturia KeyLab Mk3 werken, maar ook met andere class-compliant of vendor MIDI-bronnen zoals Fishman TriplePlay, M-Vave, RaspiMidiHub routes, MiniFreak MIDI en andere USB MIDI interfaces.

Deze story levert een veilige readiness-diagnose. Live note receive en hoorbare audio-triggering blijven buiten deze stap totdat een hardware device veilig zichtbaar is.

## Wat Nu Werkt

- `UsbMidiHardwareInputAdapter` accepteert elk zichtbaar MIDI input device.
- Device selectie kan op identifier of gedeeltelijke naam, bijvoorbeeld `Fishman`, `M-Vave` of `KeyLab`.
- De testprocedure begint altijd met `list-devices` voordat een specifiek device wordt gekozen.
- Je kunt een device per test kiezen met `--midi-device`, of een default device in de testnotities aanwijzen.
- Output-only devices worden niet als input-ready beschouwd.
- `midi list-devices --unsafe-rtmidi-scan --debuglevel light` toont bij scan-falen backenddetails en een expliciete `BLOCKER` regel.
- De handmatige hardwaretest `tests/test_hardware_midi.py` scant echte MIDI devices en faalt als er geen devices gevonden worden wanneer `PYTHON_D1_RUN_HARDWARE_MIDI=1` is gezet.
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
7. Voor de expliciete hardwaretest, draai:

```bash
PYTHON_D1_RUN_HARDWARE_MIDI=1 PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m pytest tests/test_hardware_midi.py -s
```

Deze test gaat ervan uit dat er altijd MIDI devices aangesloten zijn. Als Python geen devices vindt terwijl Logic Pro ze wel toont, faalt de test met een US-022 blocker-melding.

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
If Logic Pro shows devices but Python does not, record the Logic/Audio MIDI Setup device list and treat this as a Python MIDI backend scan issue.
No MIDI devices detected or optional MIDI backend is not installed.
No MIDI devices found.
```

- Beoordeling: US-022 is Blocked. Logic Pro shows devices but Python does not, dus dit is een Python MIDI backend scan issue en geen bewijs dat de MIDI setup leeg is.

## Impediment / Blocker

- CHATOD: CHATOD-20260709-D1PY-MVP-001 / US-022-BLOCKER-001
- Datum/tijd: 2026-07-10
- Computernaam: KodeklopperM4
- Verwachting: er zijn altijd MIDI devices aangesloten tijdens deze testfase.
- Werkelijke situatie: Logic Pro toont MIDI devices, maar Python `midi list-devices --unsafe-rtmidi-scan --debuglevel light` toont geen devices.
- Nieuw CLI-gedrag: bij scan-falen toont de CLI `MIDI backend`, optionele `MIDI backend return code`, optionele stderr/stdout en `BLOCKER: Logic Pro shows MIDI devices but Python scan returned none.`
- Nieuw testgedrag: `tests/test_hardware_midi.py` kan met `PYTHON_D1_RUN_HARDWARE_MIDI=1` een echte hardware-scan afdwingen, devices listen en falen als Python niets vindt.
- Eerste technische oorzaak gevonden en opgelost: het conflicterende pakket `rtmidi 2.5.0` stond naast `python-rtmidi 1.5.8` in dezelfde venv. Daardoor importeerde Mido de verkeerde backendmodule en miste `rtmidi.API_UNSPECIFIED`.
- Venv-herstel uitgevoerd: `rtmidi 2.5.0` verwijderd en `python-rtmidi==1.5.8` opnieuw geinstalleerd. Verificatie: `rtmidi.__version__ == 1.5.8` en `API_UNSPECIFIED=True`.
- Resterende blocker na package-herstel: `MidiInCore::initialize: error creating OS-X MIDI client object (-10833)`.
- Status: `Blocked` totdat de Python MIDI backend minstens een Logic-zichtbaar device kan listen op `KodeklopperM4` of `MuziekM4`.

Hardwaretest na venv-herstel:

```text
MIDI backend: mido/python-rtmidi
MIDI backend return code: -6
MIDI backend stderr: libc++abi: terminating due to unexpected exception of type RtMidiError: MidiInCore::initialize: error creating OS-X MIDI client object (-10833).
MIDI backend failed while scanning devices.
```

Crashlog-bevindingen:

- CHATOD: CHATOD-20260709-D1PY-MVP-001 / US-022-CRASHLOGS
- Crashlog 1: incident `35DB83DC-374A-4C19-80DE-8D43E29AF27A`, tijd `2026-07-10 17:58:47 +0200`.
- Crashlog 2: incident `FEE3C08D-0AB5-492E-BF4A-AC399EA64D14`, tijd `2026-07-10 17:58:57 +0200`.
- Proces: Python 3.12.13 via Homebrew framework, gestart onder `com.openai.codex`.
- Exception: `EXC_CRASH (SIGABRT)`, termination `Abort trap: 6`.
- Crashpad: `_rtmidi.cpython-312-darwin.so` -> `MidiInCore::getCoreMidiClientSingleton` -> `MidiInCore::initialize` -> `RtMidiIn`.
- CoreMIDI thread is aanwezig in de crashlog, wat bevestigt dat de crash optreedt tijdens native CoreMIDI input-client initialisatie.
- Conclusie: de veilige subprocess-isolatie is nodig. De hoofd-CLI mag niet zelf live CoreMIDI scanning doen totdat deze CoreMIDI/RtMidi blocker opgelost is.

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
- US-022 blijft `Blocked` totdat de Python MIDI backend minstens een echte, Logic-zichtbare MIDI input of output kan listen.
