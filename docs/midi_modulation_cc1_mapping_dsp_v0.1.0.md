# CHATOD-20260709-D1PY-MVP-001 / US-037 MIDI Modulation CC1 Mapping En DSP

Sprintnummer: Future MIDI/DAW
Doc versie: 0.1.0
Epic: EPIC-007 Future MIDI En DAW Integratie
Status: In Review

## Doel

US-037 voegt MIDI CC1 modulation toe aan sustained playback. CC1 messages worden genormaliseerd als interne `control_change` messages en sturen een eenvoudige vibrato-depth aan op actieve sustained voices.

## Implementatie

- `MidiMessage` ondersteunt `message_type="control_change"` met `control_number` en `control_value`.
- `MidiMessageNormalizer` vertaalt mido `control_change` messages naar interne MIDI messages.
- `MidiModulationMapper` mapt CC1 waarde `0..127` naar vibrato-depth in semitones.
- `StreamingMidiAudioTriggerSettings.modulation_vibrato_depth_semitones` configureert de maximale CC1 vibrato-depth.
- `StreamingMidiAudioTriggerSettings.modulation_vibrato_rate_hz` configureert de vibrato-rate.
- CLI opties: `--modulation-vibrato-depth`, default `0.25`; `--modulation-vibrato-rate`, default `5`.
- `SoundDeviceSustainedAudioPlayer.modulation(channel, depth_semitones, rate_hz)` past actieve voices op hetzelfde MIDI channel aan.
- Nieuwe sustained note-on events erven de laatst ontvangen CC1 modulation op hun MIDI channel.

Scopegrenzen:

- Alleen CC1 (`control_number=1`) wordt muzikaal toegepast.
- Alleen `--voice-mode sustained` past modulation hoorbaar toe.
- Geen filter-modulatie; CC1 stuurt in deze MVP alleen vibrato-depth.
- Geen sustain pedal.
- Geen envelope release.
- Geen GUI, AU, VST3 of Logic Component.
- Geen hardcoded MIDI hardware device names.

## Acceptatietest

Logic Pro of MIDI keyboard test:

1. Start de commandline synth.
2. Stuur MIDI naar `python-d1-synth`.
3. Houd een noot vast.
4. Beweeg mod wheel of CC1 controller.
5. Controleer dat de toon vibrato krijgt wanneer CC1 omhoog gaat en rustiger wordt wanneer CC1 omlaag gaat.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 10000 --max-control-messages 20000 --timeout 600 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --pitch-bend-range 2 --pitch-bend-channel-mode omni --modulation-vibrato-depth 0.25 --modulation-vibrato-rate 5 --debuglevel verbose
```

Verwachte CLI-indicaties:

```text
Streaming MIDI audio trigger settings: ... voice_mode=sustained ... modulation_vibrato_depth=0.25st ... modulation_vibrato_rate=5Hz ...
Received MIDI messages: ... control_change:1:96:channel=1 ...
```

Acceptatie:

- CC1 messages verschijnen in verbose output als `control_change:1:<waarde>:channel=<n>`.
- Een actieve sustained voice krijgt hoorbare vibrato wanneer CC1 boven nul staat.
- Zonder CC1 blijft sustained playback uit US-035 en pitch bend uit US-036 ongewijzigd.
- Eventuele kleine latency is toegestaan binnen US-037; professionele low-latency audio optimalisatie blijft later werk.

## Traceability

- ChatID: CHATOD-20260709-D1PY-MVP-001 / US-037
- Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-037 MIDI Modulation CC1 Mapping En DSP
- Version: 0.1.0
