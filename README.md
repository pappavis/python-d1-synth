# python-d1-synth

**A commandline-first Python synthesizer MVP for Logic Pro and MIDI performance experiments.**

`python-d1-synth` is a small, test-backed software synth prototype inspired by classic mono synth workflows. The MVP proves that a Python synth can be controlled from Logic Pro as an External MIDI destination, play audible sustained notes, handle chords, pitch bend, modulation, sustain pedal events, ADSR amplitude shaping, and load performance settings from YAML.

This is not a GUI application and not an AU/VST3 plugin yet. It is the working technical core: a clean Python package, a MIDI-to-audio route, Agile traceability, tests, docs, and a repeatable config-driven workflow.

![python-d1-synth architecture](docs/assets/python_d1_synth_architecture.svg)

## MVP Status

**MVP accepted on 2026-07-14.**

The accepted MVP can:

- Start as a normal Python commandline app.
- Render WAV files from YAML patches.
- Play sine, saw and square oscillator tones.
- Route stereo, left and right output.
- Scan MIDI devices where the local backend supports it.
- Open `python-d1-synth` as a virtual MIDI destination for Logic Pro or another DAW.
- Play notes from Logic Pro External MIDI tracks.
- Play sustained notes until note-off.
- Mix simple chords and triads.
- Handle duplicate MIDI event suppression.
- Apply pitch bend, CC1 vibrato modulation, CC64 sustain pedal handling, release fade and ADSR amplitude settings.
- Load performance defaults from `examples/midi_performance_patch.yaml`.
- Let commandline flags override YAML settings when needed.

## Who This Is For

This repo is written for three audiences:

- **Logic Pro users** who want to try a Python synth without learning plugin development first.
- **Python developers** who want a class-based, tested audio/MIDI prototype.
- **Technical reviewers** who want to see a disciplined MVP with traceable stories, tests and docs.

If you are comfortable in Logic Pro but not in Terminal, follow the short path below and copy commands exactly. The commandline part is intentionally small.

## Quick Start For Logic Pro Users

### 1. Install Python

Install Python 3.11 or newer from [python.org](https://www.python.org/downloads/) or your preferred package manager.

Check it:

```bash
python --version
```

On some Windows systems, use:

```powershell
py --version
```

### 2. Get The Project

```bash
git clone https://github.com/pappavis/python-d1-synth.git
cd python-d1-synth
```

If you downloaded a ZIP instead of using Git, unzip it and open Terminal or PowerShell in the `python-d1-synth` folder.

### 3. Create A Local Virtual Environment

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[midi]"
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[midi]"
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then open a new PowerShell window and activate `.venv` again.

### 4. Choose Your Audio Output In YAML

Open:

```text
examples/midi_performance_patch.yaml
```

Find:

```yaml
audio_device: null
```

You have two choices:

- Leave it as `null` to use the system default audio output.
- Replace `null` with the exact name of your preferred output device.

You can list available audio devices with:

```bash
python -m synth audio list-devices --debuglevel light
```

Example YAML shape:

```yaml
midi:
  performance:
    port_name: python-d1-synth
    audio_device: null
    voice_mode: sustained
    run_until_interrupted: true
```

Keep device names in YAML or pass them as temporary commandline overrides. They are not hardcoded in the application.

### 5. Start The Synth

```bash
python -m synth midi play-stream --config examples/midi_performance_patch.yaml
```

Leave this command running. It opens the virtual MIDI destination named `python-d1-synth`.

Stop it later with `Ctrl-C`.

### 6. Route Logic Pro To The Synth

In Logic Pro:

1. Create a new track.
2. Choose `MIDI`.
3. Choose `External MIDI`.
4. Set `MIDI Destination` to `python-d1-synth`.
5. Set `MIDI Channel` to `All` or `1`.
6. Create a small MIDI region with a few notes, or use Musical Typing.
7. Press Play.

Expected result: you hear the Python synth through your configured audio output.

## Useful Commands

Run the YAML-driven performance patch:

```bash
python -m synth midi play-stream --config examples/midi_performance_patch.yaml
```

Override the YAML audio device for one run:

```bash
python -m synth midi play-stream --config examples/midi_performance_patch.yaml --audio-device "<your-audio-device-name>"
```

Use verbose diagnostics:

```bash
python -m synth midi play-stream --config examples/midi_performance_patch.yaml --debuglevel verbose
```

Render a WAV demo:

```bash
python -m synth render examples/patch.yaml --output outputs/demo.wav --debuglevel light
```

Play a simple note without Logic:

```bash
python -m synth play --note C3 --duration 1.0 --channel stereo --debuglevel light
```

Play a small test sequence:

```bash
python -m synth play --testsequence "ACGD" --duration 0.25 --debuglevel light
```

List audio devices:

```bash
python -m synth audio list-devices --debuglevel light
```

List MIDI devices:

```bash
python -m synth midi list-devices --unsafe-rtmidi-scan --debuglevel light
```

## YAML First, CLI When Needed

The preferred MVP workflow is:

1. Put stable defaults in `examples/midi_performance_patch.yaml`.
2. Start with `python -m synth midi play-stream --config examples/midi_performance_patch.yaml`.
3. Use commandline flags only for temporary overrides.

Precedence is:

1. Explicit commandline flag.
2. YAML value.
3. Built-in safe default.

That means this command temporarily overrides the YAML voice mode and debug level:

```bash
python -m synth midi play-stream --config examples/midi_performance_patch.yaml --voice-mode gated --debuglevel verbose
```

## What The MVP Proves

The MVP proves the core route end to end:

```text
Logic Pro MIDI region
  -> virtual MIDI destination python-d1-synth
  -> MIDI message normalizer
  -> NoteEvent / sustained voice model
  -> oscillator and voice mixer
  -> sounddevice audio output
```

It also proves the working process:

- User stories `US-001` through `US-042` are documented.
- Acceptance criteria and story status are tracked.
- The Kanban backlog is generated as an XLSX workbook.
- Tests cover the core behavior with fake backends where hardware is not available.
- Hardware and Logic Pro behavior are recorded as product-owner acceptance evidence.

## Current Limitations

The MVP is intentionally focused. These are not defects:

- It is not an AU, VST3 or Logic Component plugin.
- It is not a standalone packaged desktop app yet.
- It has no graphical synth panel yet.
- It does not yet model a full Behringer D / Model D style subtractive voice architecture.
- Low-latency production audio performance will need a deeper audio-engine pass.
- Windows support is installable in principle, but real MIDI/audio behavior must still be validated on a Windows machine.

## Documentation Map

Core project artifacts:

- [MVP Scope](docs/mvp_scope.md)
- [User Stories](docs/user_stories.md)
- [Acceptance Criteria](docs/acceptance_criteria.md)
- [Sprint Lessons Learned And Review](docs/sprint_lessons_learned_review_v0.1.0.md)
- [MVP Sprint Review](docs/mvp_sprint_review_v0.1.0.md)
- [MVP Retrospective](docs/mvp_retrospective_v0.1.0.md)
- [Kanban Workbook](outputs/CHATOD-20260709-D1PY-MVP-001/python_d1_synth_sprint_1_kanban_backlog.xlsx)

Important MIDI / DAW docs:

- [MIDI Learning Path](docs/midi_learning_path_v0.1.0.md)
- [Virtual MIDI Port For Logic/DAW](docs/virtual_midi_port_logic_daw_v0.1.0.md)
- [Logic/DAW Virtual MIDI Audio Trigger](docs/virtual_midi_audio_trigger_v0.1.0.md)
- [Live/Streaming MIDI Playback Loop](docs/live_streaming_midi_playback_loop_v0.1.0.md)
- [Sustained Note Audio Engine](docs/sustained_note_audio_engine_v0.1.0.md)
- [MIDI Pitch Bend Mapping](docs/midi_pitch_bend_mapping_dsp_v0.1.0.md)
- [MIDI Modulation CC1 Mapping](docs/midi_modulation_cc1_mapping_dsp_v0.1.0.md)
- [MIDI Performance Patch YAML Config](docs/midi_performance_patch_yaml_config_v0.1.0.md)

## Development Workflow

Run tests:

```bash
python -m pytest
```

Run only documentation checks:

```bash
python -m pytest tests/test_docs.py
```

Run the real hardware MIDI scan only when hardware is connected:

```bash
PYTHON_D1_RUN_HARDWARE_MIDI=1 python -m pytest tests/test_hardware_midi.py -s
```

The codebase follows the project rules established during the MVP:

- Class-based implementation.
- No global application state.
- Tests for red/green story work.
- Traceability in code and docs for changed story work.
- Runtime device discovery and YAML config instead of hardcoded hardware names.

## Suggested Next Sprint

The next sprint should choose one clear product direction:

- **Synth character:** filter cutoff/resonance, envelope-to-filter, better oscillator behavior.
- **Usability:** small desktop UI or patch manager.
- **Delivery:** packaged macOS/Windows app.
- **Plugin path:** AU/VST3 feasibility spike.
- **Hardware path:** CircuitPython/ESP32 feasibility spike.

The MVP is deliberately solid enough to make that choice from a working baseline.

## License

MIT. See [LICENSE](LICENSE).
