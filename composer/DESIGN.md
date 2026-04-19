# Composer Module Design

## Overview
The `composer` module provides classes to build, manage, and render musical notation (standard Western staves, notes, key signatures, and time signatures) onto a screen using CircuitPython's `displayio` framework. This allows building dynamic, on-screen musical notation for educational tools, sheet music reading, or scale drilling.

## Core Classes

### `Note`
Represents a single playable pitch. Key attributes: `name`, `midi_number`, `fingerings` (hardware button masks), `ledger_line` (fractional staff position — see Staff coordinate system below), and `accidental` (`"sharp"`, `"flat"`, `"natural"`, or `None`).

### `TimedNote`
A `Note` paired with a `Duration` (`"whole"`, `"half"`, `"quarter"`, `"eighth"`). This is the unit passed to `Staff.update_sequence`.

### `KeySignature`
Defines the tonal center of the piece, determining which notes are naturally sharp or flat.
- Holds a sorted list of accidental notes (in standard circle-of-fifths order) drawn in the static key-signature block at the staff head.
- Can filter notes by octave (e.g., 3rd or 4th octave) to assist with scale drills. *(not yet implemented)*
- Drives per-note accidental suppression during rendering: if a note's accidental matches the key signature no decoration is drawn; if the key signature implies an accidental but the played note is natural, a natural sign is drawn instead.

### `TimeSignature`
Defines the rhythmic structure (e.g., 4/4, 3/4). **Not yet implemented** — `Staff` currently hardcodes 4/4.
- Will determine measure boundaries and beat counts.
- Will provide the `beats_per_measure` value used to divide available horizontal space into beat slots.

### `Staff`
The primary visual container. Inherits from `displayio.Group` so it can be positioned on screen with `.x` / `.y` and appended directly to a display root group.

**Constructor**: `Staff(width, config, key_signature=C_MAJOR, time_signature=None)`
- `width` — pixel width of the staff; determines how wide the staff lines are and how much horizontal space notes are distributed across.
- `config` — provides `fg_color` and `bg_color` via `config.color_data`, applied to all sprite palettes at load time.
- `key_signature` — drives both the static accidental block and per-note accidental decoration. Defaults to C major (no accidentals).

**Coordinate system**
- `LEDGER_SPACING = 16px` — distance between adjacent staff lines, also the unit of vertical note movement.
- `HEIGHT = 13 * LEDGER_SPACING = 208px` — fixed total height; accommodates 4 ledger lines above the staff, the 5 standard lines, and 4 ledger lines below.
- `staff_y_start = 4 * LEDGER_SPACING` — the top staff line sits 64px from the group's top edge, leaving room for high notes.
- `ledger_line` coordinate: `0.0` = E4 (bottom staff line), `4.0` = F5 (top staff line). Each whole unit is one line (16px); each 0.5 step is one space (8px). Values below 0 are below the staff (e.g., C4 = -1.0); values above 4 are above it (e.g., A5 = 5.0).

**Static layer** (`static_group`) — drawn once on construction, never modified:
- Five 1px-tall staff lines spanning the full `width`.
- Treble clef image, vertically centered on the staff.
- Key signature accidentals, starting just after the clef (~x=32). Each accidental sprite is placed using a canonical treble-clef slot lookup (`SHARP_SLOTS` / `FLAT_SLOTS`) that maps note letters to their standard vertical positions, independent of any individual note's `ledger_line` value.

**Dynamic layer** (`dynamic_group`) — pooled sprites updated on every `update_sequence` call:
- Note sprites (from the note sprite sheet).
- Per-note accidental sprites (from the accidental sprite sheet), positioned just to the left of the note head when needed.
- Extra ledger line sprites for notes outside the 5 standard lines. Required lines are computed from the note's `ledger_line` value: integer positions between the staff boundary and the note (e.g., C4 at -1.0 needs one line at -1; C6 at 6.0 needs lines at 5 and 6).

**Horizontal layout** — `update_sequence` computes a `beat_width` from the available space (after clef and key signature) divided by 4 (beats per measure). Each note is centered within its proportional beat slot: a whole note is centered across the full measure, a half note in its half, etc.

**Public API**
- `update_sequence(list[TimedNote])` — renders a measure. Safe to call repeatedly; hides all pooled sprites first, then reuses them from index 0.
- `show_note(note, duration)` — convenience wrapper that calls `update_sequence` with a single-element list.

## Sprite Assets

| Asset | Path | Layout |
|---|---|---|
| Treble clef | `data/img/treble_clef_white.png` | single image |
| Accidentals | `data/img/accidental_sprite_sheet.png` | 3 × 1 tiles (14×42 px each): flat(0), sharp(1), natural(2) |
| Notes | `data/img/note_sprite_sheet.png` | 5 × 2 tiles (30×48 px each): top row = eighth(0), quarter(1), half(2), whole(3); bottom row = rests |

All sprites are white-on-transparent; the foreground color is applied via palette at load time so the color scheme is fully driven by `config`.

**Pin points** — each sprite has an (x, y) pixel offset representing the note head center within the tile. This point is aligned to the target staff Y coordinate when positioning the sprite. Current values: `pin_x = 8`, `pin_y = 40` for all note durations. Accidental sprites have their own per-type `pin_y` values tuned to the bowl/crosshair of each glyph.

## Architecture & Performance

Running on microcontrollers with `displayio`, memory fragmentation and redraw performance are the primary constraints.

**Static vs. dynamic grouping** — separating the staff into a static and dynamic `displayio.Group` means the lines, clef, and key signature are never redrawn during playback. `displayio` only redraws the bounds of sprites that actually moved.

**Sprite sheets** — loading a single sprite sheet and selecting tiles via `TileGrid` index is far more RAM-efficient than loading individual image files per symbol.


**Object pooling** — dynamically allocating and garbage-collecting `TileGrid` objects during playback causes stuttering and memory exhaustion. `Staff` pre-allocates fixed pools at construction time:
- 8 note sprites
- 8 accidental sprites
- 24 ledger-line sprites (up to 3 per note × 8 notes)

To show a sprite: move it to the target position and update its tile index. To hide it: move it off-screen (`x = -1000`). Sprites already off-screen are not checked before hiding — the unconditional write is cheaper than a read-and-branch for a pool this small, and off-screen tiles generate no pixel work during refresh.

## Rendering Pipeline

1. Instantiate `Staff(width, config, key_signature)`. The static layer is drawn immediately.
2. Call `staff.update_sequence(list[TimedNote])` whenever the displayed measure changes.
3. All pooled sprites are hidden; pool indices reset to 0.
4. `content_x` is computed as clef width (32px) + key signature width + 8px padding. `beat_width = (staff.width - content_x) / 4`.
5. For each `TimedNote`: compute the beat-centered X, compute Y from `note.ledger_line`, draw any required extra ledger lines, draw a per-note accidental if needed, place the note sprite.
6. Only the bounds of moved sprites are redrawn by `displayio`.

`staff.show_note(note, duration)` is a convenience wrapper that calls `update_sequence` with a single-element list.

## Testing
Use `test/display_utils.py` (`prep_display`, `show_and_wait`) to render a `Staff` into a PyGame window on desktop. Tests live in `test/staff_notes_test.py` and cover static lines, key signatures, note placement, ledger lines, and live update loops. Headless golden image comparison can be done via `save_to_image()`.