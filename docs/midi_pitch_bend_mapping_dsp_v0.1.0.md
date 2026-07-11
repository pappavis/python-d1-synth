# CHATOD-20260709-D1PY-MVP-001 / US-036 MIDI Pitch Bend Mapping En DSP

Sprintnummer: Future MIDI/DAW
Doc versie: 0.1.0
Epic: EPIC-007 Future MIDI En DAW Integratie
Status: In Review

## Doel

US-036 voegt MIDI pitch bend toe aan sustained playback. Pitch bend messages worden per MIDI channel gemapt naar actieve sustained voices, zodat de oscillatorfrequentie vloeiend omhoog of omlaag kan buigen terwijl een noot klinkt.

## Implementatie

- `MidiMessage` ondersteunt `message_type="pitch_bend"` met `pitch_bend_value` in bereik `-8192..8191`.
- `MidiMessageNormalizer` vertaalt mido `pitchwheel` messages naar interne `pitch_bend` messages.
- `MidiPitchBendMapper` mapt raw pitch bend waarden naar semitone-offsets en frequentieratio's.
- `StreamingMidiAudioTriggerSettings.pitch_bend_range_semitones` configureert het bendbereik.
- CLI optie: `--pitch-bend-range`, default `2.0`.
- CLI optie: `--pitch-bend-channel-mode same|omni`, default `same`.
- CLI optie: `--max-control-messages`, default `1024`, geeft pitch bend/control bursts extra ruimte naast de note-event testlimiet.
- `SoundDeviceSustainedAudioPlayer.pitch_bend(channel, semitones)` past actieve voices op het gekozen MIDI channel aan.
- Nieuwe sustained note-on events erven de laatst ontvangen pitch bend op hun MIDI channel.
- In `omni` mode past een ontvangen pitch bend message de bend toe op alle actieve sustained voice channels. Dit is bedoeld voor MVP/diagnose-routes waar de controller of DAW note events en pitch bend events op verschillende MIDI channels aanlevert.

Scopegrenzen:

- Alleen `--voice-mode sustained` past pitch bend muzikaal toe.
- Geen MIDI modulation/CC1; dat is US-037.
- Geen sustain pedal.
- Geen envelope release.
- Geen GUI, AU, VST3 of Logic Component.
- Geen hardcoded MIDI hardware device names.

## Acceptatietest

Logic Pro of MIDI keyboard test:

1. Start de commandline synth.
2. Stuur MIDI naar `python-d1-synth`.
3. Houd een noot vast.
4. Beweeg pitch bend wheel of pitch bend strip.
5. Controleer dat de toon hoorbaar omhoog/omlaag buigt.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 30 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --debuglevel verbose
```

SMK37/Logic cross-channel test:

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 30 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --debuglevel verbose
```

Verwachte CLI-indicaties:

```text
Streaming MIDI audio trigger settings: ... voice_mode=sustained ... pitch_bend_range=2st ... pitch_bend_channel_mode=omni ...
Received MIDI messages: ... pitch_bend:4096:channel=1 ...
```

Acceptatie:

- Pitch bend messages verschijnen in verbose output.
- Een actieve sustained voice buigt hoorbaar in toonhoogte.
- Bend werkt per MIDI channel.
- `--pitch-bend-channel-mode omni` maakt pitch bend hoorbaar wanneer note events en pitch bend events op verschillende channels binnenkomen.
- Pitch bend bursts stoppen de stream niet meer na de eerste `--max-messages 32`; `--max-control-messages` geeft control messages aparte speelruimte.
- Zonder pitch bend blijft sustained playback uit US-035 ongewijzigd.
- Eventuele kleine latency is toegestaan binnen US-036; modulation/CC1 blijft US-037.

## Traceability

- ChatID: CHATOD-20260709-D1PY-MVP-001 / US-036-IMPEDIMENT-001
- Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-036 MIDI Pitch Bend Mapping En DSP
- Version: 0.1.0
