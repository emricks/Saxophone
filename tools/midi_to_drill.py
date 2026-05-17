"""Convert a MIDI file to a drill payload entry.

Workstation-only utility (uses `mido` — `pip install mido`, also covered by
`make deps`). Not deployed to the device; `tools/` isn't in the Makefile's
deploy allow-list.

Sheet Music Scanner exports MusicXML and MIDI for the same source page.
The MusicXML export has been unreliable for these lessons (lesson body
sometimes comes through as leading whole rests). The MIDI export is the
ground truth — the in-app playback uses it directly — so this tool reads
MIDI.

Typical usage:

    # Summarize tracks, BPM, key signature, etc.
    python tools/midi_to_drill.py inspect path/to/lesson.mid

    # Emit the notes list for a specific track as a Python literal
    python tools/midi_to_drill.py notes path/to/lesson.mid --track 2

    # Emit a full drill(...) call ready to drop into menu_config.py
    python tools/midi_to_drill.py drill path/to/lesson.mid --track 2 \
            --text "Rubank E Lesson 2" --mode none

Notes / behavior:

- Alto-sax transposition: MIDI files from Sheet Music Scanner encode concert
  pitch. The alto sounds a major 6th below its written pitch, so we shift
  UP 9 semitones to recover the written pitch (which is what our Notes
  table is keyed on). Override with `--transpose N` if a file is already in
  written pitch.
- Rests: MIDI doesn't encode rests explicitly, so gaps between note_off and
  the next note_on are bucketized into the closest whole/half/quarter/eighth
  rests.
- Unsupported durations (16th, 32nd, dotted, oddly-quantized) are dropped
  with a printed warning so you can see what was lost.
"""

import argparse
import os
import sys

import mido


# Standard durations we can render: (beats, token). Order matters for the
# greedy bucketing in `bucketize_beats`.
DURATION_BUCKETS = [
    (4.0, "WHOLE"),
    (2.0, "HALF"),
    (1.0, "QUARTER"),
    (0.5, "EIGHTH"),
]

# How close (relative) a measured beat count must be to a bucket to count
# as that duration. 0.85 beats at tolerance 0.25 still rounds to QUARTER.
BUCKET_TOLERANCE = 0.25

# MIDI pitch class -> (step, alter). Two spellings; we default to sharps.
PITCH_CLASS_SHARPS = [
    ("C", 0), ("C", 1), ("D", 0), ("D", 1), ("E", 0), ("F", 0),
    ("F", 1), ("G", 0), ("G", 1), ("A", 0), ("A", 1), ("B", 0),
]
PITCH_CLASS_FLATS = [
    ("C", 0), ("D", -1), ("D", 0), ("E", -1), ("E", 0), ("F", 0),
    ("G", -1), ("G", 0), ("A", -1), ("A", 0), ("B", -1), ("B", 0),
]

ALTO_TRANSPOSE_SEMITONES = 9


def midi_to_note_name(midi_note, prefer_flats=False):
    pc = midi_note % 12
    octave = (midi_note // 12) - 1
    table = PITCH_CLASS_FLATS if prefer_flats else PITCH_CLASS_SHARPS
    step, alter = table[pc]
    if alter == 1:
        return f"{step}_SHARP_{octave}"
    if alter == -1:
        return f"{step}_FLAT_{octave}"
    return f"{step}_{octave}"


def bucketize_beats(beats):
    """Greedy-bucket a beat count into a list of duration tokens. Returns
    (tokens, leftover_beats). leftover > 0 means there's a tail we couldn't
    fit (e.g. 16th or 32nd notes)."""
    out = []
    remaining = beats
    for ref, token in DURATION_BUCKETS:
        while remaining >= ref - ref * BUCKET_TOLERANCE:
            # Close enough to one of this size, consume it.
            out.append(token)
            remaining -= ref
            if remaining < 0:
                remaining = 0
    return out, remaining


def find_tempo_and_meta(mid):
    """Returns (bpm, time_sig, key_sig) by scanning track 0 (conductor)."""
    bpm = None
    time_sig = None
    key_sig = None
    for msg in mid.tracks[0]:
        if msg.type == "set_tempo" and bpm is None:
            bpm = int(round(60_000_000 / msg.tempo))
        elif msg.type == "time_signature" and time_sig is None:
            time_sig = (msg.numerator, msg.denominator)
        elif msg.type == "key_signature" and key_sig is None:
            key_sig = msg.key
    # Some MIDI files put tempo on every track. Fall back if track 0 had none.
    if bpm is None:
        for track in mid.tracks[1:]:
            for msg in track:
                if msg.type == "set_tempo":
                    bpm = int(round(60_000_000 / msg.tempo))
                    break
            if bpm is not None:
                break
    return bpm, time_sig, key_sig


def collect_note_events(track):
    """Returns [(start_tick, end_tick, midi_note)] for note pairs in `track`,
    sorted by start_tick."""
    open_notes = {}
    events = []
    abs_t = 0
    for msg in track:
        abs_t += msg.time
        is_on = msg.type == "note_on" and msg.velocity > 0
        is_off = msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0)
        if is_on:
            if msg.note in open_notes:
                events.append((open_notes[msg.note], abs_t, msg.note))
            open_notes[msg.note] = abs_t
        elif is_off:
            if msg.note in open_notes:
                events.append((open_notes.pop(msg.note), abs_t, msg.note))
    events.sort(key=lambda e: (e[0], e[1]))
    return events


def _ticks_per_measure(mid):
    """Computes ticks per measure from ticks_per_beat and the time signature
    on track 0. Defaults to 4 beats/measure if no time signature is present."""
    beats_per_measure = 4
    for msg in mid.tracks[0]:
        if msg.type == "time_signature":
            beats_per_measure = msg.numerator
            break
    return mid.ticks_per_beat * beats_per_measure


def _resolve_tick_range(mid, measures_arg, from_tick, until_tick, measure_anchor=0):
    """measures_arg of the form 'M-N' (inclusive, 1-based) wins over
    from_tick/until_tick. measure_anchor is the MIDI tick where the score's
    measure 1 actually starts — Sheet Music Scanner often inserts pickup
    content (sample staves, ornaments misread as notes) that pushes the real
    exercise back. With anchor=X, --measures 1-80 maps to ticks X..X+80*tpm.
    Returns (from_tick, until_tick) — either can be None."""
    if measures_arg:
        first, _, last = measures_arg.partition("-")
        first = int(first)
        last = int(last) if last else first
        tpm = _ticks_per_measure(mid)
        from_tick = measure_anchor + (first - 1) * tpm
        until_tick = measure_anchor + last * tpm  # exclusive: end of measure `last`
    return from_tick, until_tick


def extract_notes(mid, track_index, transpose, prefer_flats=False,
                  from_tick=None, until_tick=None):
    """Returns (notes_list, dropped_list). notes_list is in drill payload
    format; dropped_list contains human-readable reasons for skipped events."""
    track = mid.tracks[track_index]
    ticks_per_beat = mid.ticks_per_beat
    events = collect_note_events(track)
    if from_tick is not None:
        events = [e for e in events if e[0] >= from_tick]
    if until_tick is not None:
        events = [e for e in events if e[0] < until_tick]

    out = []
    dropped = []
    # The first rest is anchored to from_tick (or 0) so that an excerpt
    # starting at measure N doesn't carry over a phantom rest from offset 0.
    last_end = from_tick if from_tick is not None else 0

    for start, end, midi_note in events:
        gap_ticks = start - last_end
        if gap_ticks > 0:
            gap_beats = gap_ticks / ticks_per_beat
            tokens, leftover = bucketize_beats(gap_beats)
            for token in tokens:
                out.append("REST" if token == "QUARTER" else f"REST:{token}")
            if leftover > 0.05:
                dropped.append(f"rest {leftover:.3f}b at tick {last_end}")

        dur_beats = (end - start) / ticks_per_beat
        tokens, leftover = bucketize_beats(dur_beats)
        if not tokens:
            dropped.append(f"note {midi_note} dur {dur_beats:.3f}b at tick {start}")
            last_end = end
            continue
        # Split a tied note across multiple tokens. The drill layer treats
        # consecutive same-pitch entries as separate items, which is fine
        # for tied wholes / halves but not musically perfect — we accept it
        # rather than dropping otherwise-valid material.
        written = midi_note + transpose
        name = midi_to_note_name(written, prefer_flats=prefer_flats)
        for token in tokens:
            out.append(name if token == "QUARTER" else f"{name}:{token}")
        if leftover > 0.05:
            dropped.append(f"note {midi_note} leftover {leftover:.3f}b at tick {start}")

        last_end = end

    # Trailing silence: if the extraction window extends past the last note,
    # emit rests for the gap so the drill's total duration matches the score.
    if until_tick is not None and last_end < until_tick:
        gap_beats = (until_tick - last_end) / ticks_per_beat
        tokens, leftover = bucketize_beats(gap_beats)
        for token in tokens:
            out.append("REST" if token == "QUARTER" else f"REST:{token}")
        if leftover > 0.05:
            dropped.append(f"trailing rest {leftover:.3f}b")

    return out, dropped


def _format_drill_call(text, name, key, notes, mode, bpm):
    parts = [f'    drill("{text}", "{key}",']
    notes_lit = ", ".join(f'"{n}"' for n in notes)
    parts.append(f"          [{notes_lit}],")
    extras = []
    if name and name != text:
        extras.append(f'name="{name}"')
    if mode:
        extras.append(f'mode="{mode}"')
    if bpm:
        extras.append(f"bpm={bpm}")
    if extras:
        parts.append("          " + ", ".join(extras) + "),")
    else:
        parts[-1] = parts[-1].rstrip(",") + "),"
    return "\n".join(parts)


def cmd_inspect(args):
    mid = mido.MidiFile(args.path)
    bpm, time_sig, key_sig = find_tempo_and_meta(mid)
    tpm = _ticks_per_measure(mid)
    print(f"File: {os.path.basename(args.path)}")
    print(f"ticks_per_beat: {mid.ticks_per_beat}, ticks_per_measure: {tpm}")
    print(f"BPM (from tempo): {bpm}")
    print(f"Time signature: {time_sig}")
    print(f"Key signature: {key_sig}")
    print(f"Tracks ({len(mid.tracks)}):")
    for i, track in enumerate(mid.tracks):
        note_events = collect_note_events(track)
        if not note_events:
            type_summary = {}
            for msg in track:
                type_summary[msg.type] = type_summary.get(msg.type, 0) + 1
            print(f"  [{i}] {track.name!r}: {dict(type_summary)}")
            continue
        first_start = note_events[0][0]
        last_end = max(e[1] for e in note_events)
        notes_in_track = [e[2] for e in note_events]
        lo, hi = min(notes_in_track), max(notes_in_track)
        first_measure = first_start // tpm + 1
        last_measure = (last_end - 1) // tpm + 1
        print(f"  [{i}] {track.name!r}: {len(note_events)} notes, "
              f"measures {first_measure}..{last_measure} (ticks {first_start}..{last_end}), "
              f"midi {lo}..{hi} concert, "
              f"+9 written {lo + ALTO_TRANSPOSE_SEMITONES}..{hi + ALTO_TRANSPOSE_SEMITONES}")


def cmd_notes(args):
    mid = mido.MidiFile(args.path)
    from_tick, until_tick = _resolve_tick_range(
        mid, args.measures, args.from_tick, args.until_tick,
        measure_anchor=args.measure_anchor,
    )
    notes, dropped = extract_notes(
        mid, args.track,
        transpose=args.transpose if args.transpose is not None else ALTO_TRANSPOSE_SEMITONES,
        prefer_flats=args.flats,
        from_tick=from_tick,
        until_tick=until_tick,
    )
    if dropped:
        print(f"# dropped {len(dropped)} event(s):", file=sys.stderr)
        for d in dropped[:20]:
            print(f"#   {d}", file=sys.stderr)
        if len(dropped) > 20:
            print(f"#   ... and {len(dropped) - 20} more", file=sys.stderr)
    print(notes)


def cmd_drill(args):
    mid = mido.MidiFile(args.path)
    bpm, _ts, _ks = find_tempo_and_meta(mid)
    bpm = args.bpm or bpm
    from_tick, until_tick = _resolve_tick_range(
        mid, args.measures, args.from_tick, args.until_tick,
        measure_anchor=args.measure_anchor,
    )
    notes, dropped = extract_notes(
        mid, args.track,
        transpose=args.transpose if args.transpose is not None else ALTO_TRANSPOSE_SEMITONES,
        prefer_flats=args.flats,
        from_tick=from_tick,
        until_tick=until_tick,
    )
    if dropped:
        print(f"# dropped {len(dropped)} event(s):", file=sys.stderr)
        for d in dropped[:20]:
            print(f"#   {d}", file=sys.stderr)
        if len(dropped) > 20:
            print(f"#   ... and {len(dropped) - 20} more", file=sys.stderr)
    print(_format_drill_call(
        text=args.text or os.path.splitext(os.path.basename(args.path))[0],
        name=args.name,
        key=args.key,
        notes=notes,
        mode=args.mode,
        bpm=bpm,
    ))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    p_inspect = sub.add_parser("inspect", help="summarize tracks, tempo, etc.")
    p_inspect.add_argument("path")
    p_inspect.set_defaults(func=cmd_inspect)

    p_notes = sub.add_parser("notes", help="emit the notes list as a Python literal")
    p_notes.add_argument("path")
    p_notes.add_argument("--track", type=int, required=True, help="track index to extract from")
    p_notes.add_argument("--transpose", type=int, default=None,
                          help=f"override semitone shift (default: +{ALTO_TRANSPOSE_SEMITONES} for alto sax)")
    p_notes.add_argument("--flats", action="store_true",
                          help="prefer flat spellings over sharp spellings")
    p_notes.add_argument("--from-tick", type=int, default=None,
                          help="skip events whose start tick is before this")
    p_notes.add_argument("--until-tick", type=int, default=None,
                          help="stop at this absolute tick (use to drop a duet section at the end)")
    p_notes.add_argument("--measures", default=None,
                          help="inclusive 1-based measure range 'M-N' (computed from ticks/beat + time sig); "
                               "overrides --from-tick/--until-tick")
    p_notes.add_argument("--measure-anchor", type=int, default=0,
                          help="MIDI tick where the score's measure 1 starts (default 0). "
                               "Use to skip OCR pickup garbage so --measures works in score terms.")
    p_notes.set_defaults(func=cmd_notes)

    p_drill = sub.add_parser("drill", help="emit a full drill(...) helper call")
    p_drill.add_argument("path")
    p_drill.add_argument("--track", type=int, required=True, help="track index to extract from")
    p_drill.add_argument("--transpose", type=int, default=None,
                          help=f"override semitone shift (default: +{ALTO_TRANSPOSE_SEMITONES} for alto sax)")
    p_drill.add_argument("--flats", action="store_true")
    p_drill.add_argument("--from-tick", type=int, default=None,
                          help="skip events whose start tick is before this")
    p_drill.add_argument("--until-tick", type=int, default=None,
                          help="stop at this absolute tick")
    p_drill.add_argument("--measures", default=None,
                          help="inclusive 1-based measure range 'M-N'; overrides --from-tick/--until-tick")
    p_drill.add_argument("--measure-anchor", type=int, default=0,
                          help="MIDI tick where the score's measure 1 starts (default 0). "
                               "Use to skip OCR pickup garbage so --measures works in score terms.")
    p_drill.add_argument("--text", help="menu label (default: file stem)")
    p_drill.add_argument("--name", help="drill 'name' (default: same as text)")
    p_drill.add_argument("--key", default="C_MAJOR", help="key signature (default: C_MAJOR)")
    p_drill.add_argument("--mode", default="none", help="drill mode (default: none)")
    p_drill.add_argument("--bpm", type=int, help="override the BPM from the MIDI")
    p_drill.set_defaults(func=cmd_drill)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()