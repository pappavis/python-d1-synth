# CHATOD-20260709-D1PY-MVP-001 / US-035 Sustained Note Audio Engine

Sprintnummer: Future MIDI/DAW
Doc versie: 0.1.0
Epic: EPIC-007 Future MIDI En DAW Integratie
Status: In Review

## Doel

US-035 voegt een sustained streaming voice mode toe aan `midi play-stream`, zodat `note_on` een actieve hoorbare voice start en `note_off` die voice stopt. Hiermee lossen we de US-033/US-034 beperking op waarbij een vastgehouden toets nog als kort pulse-nootje klonk.

## Implementatie

- `StreamingVoiceMode.SUSTAINED` voegt CLI voice mode `--voice-mode sustained` toe.
- `SoundDeviceSustainedAudioPlayer` opent een `sounddevice.OutputStream` en mixt actieve voices in de audiocallback.
- `SustainedAudioPlayerSettings` bevat sample-rate, waveform, amplitude, channel en audio device.
- `SustainedVoiceState` bewaart frequentie, velocity en oscillatorfase per actieve voice.
- `StreamingMidiAudioTrigger` vertaalt `note_on` naar `sustained_audio_player.note_on(...)`.
- `note_off` of `note_on` met velocity `0` vertaalt naar `sustained_audio_player.note_off(...)`.
- Open voices worden veilig gestopt wanneer de bounded run eindigt of wanneer cleanup nodig is.
- Duplicate filtering en chord-window blijven bestaan voor MIDI input hygiëne en polyfone note-on groepen.

Scopegrenzen:

- Geen sustain pedal.
- Geen envelope release.
- Geen MIDI pitch bend; dat is US-036.
- Geen MIDI modulation/CC1; dat is US-037.
- Geen GUI, AU, VST3 of Logic Component.
- Geen hardcoded MIDI hardware device names.

## Acceptatietest

Logic Pro of MIDI keyboard test:

1. Start de commandline synth.
2. Stuur MIDI naar `python-d1-synth`.
3. Druk C3 ongeveer 2 seconden in.
4. Laat C3 los.
5. Controleer dat de toon ongeveer 2 seconden hoorbaar blijft en niet alleen als korte pulse speelt.

```bash
PYTHONPATH=src /Volumes/data1/michiele/venv/venv3.12/bin/python -m synth midi play-stream --port-name python-d1-synth --audio-device "Scarlett 8i6 USB" --max-messages 32 --timeout 30 --note-duration 0.25 --voice-mode sustained --dedupe-window 0.03 --chord-window 0.08 --debuglevel verbose
```

Verwachte CLI-indicaties:

```text
Sustained MVP note: note_on starts a streaming voice and note_off stops it
Streaming MIDI audio trigger settings: ... voice_mode=sustained ...
Streamed note durations: C3@.../2...
```

Acceptatie:

- Een vastgehouden toets blijft hoorbaar tot `note_off`.
- Meerdere gelijktijdige voices kunnen tegelijk actief zijn.
- `Streamed note durations` blijft note-on/note-off duur rapporteren.
- Ctrl-C blijft de commandline afbreken via bestaande streaming interrupt handling.
- Eventuele kleine latency is toegestaan binnen US-035; professionele low-latency audio optimalisatie blijft later werk.

## Traceability

- ChatID: CHATOD-20260709-D1PY-MVP-001 / US-035
- Backlog: Sprint 1 Kanban Backlog / Future MIDI/DAW Backlog
- Epic: EPIC-007 Future MIDI En DAW Integratie
- User Story: US-035 Sustained Note Audio Engine
- Version: 0.1.0

