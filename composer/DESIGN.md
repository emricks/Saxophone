# Composer Module Design

## Overview
The `composer` module provides classes to build, manage, and draw musical notation (specifically standard Western musical staves, notes, key signatures, and time signatures) onto a screen using CircuitPython's `displayio` framework. This allows building dynamic, on-screen musical notation for educational tools, sheet music reading, or scale drilling.

## Core Concepts

### `Note`
- **Purpose**: Represents a single playable musical note.
- **Attributes**: `name`, `midi_number`, `fingerings` (hardware button masks), `ledger_line` (its vertical position on the staff), and `accidental` (sharp/flat).
- **Current State**: Implemented in `notes.py`.

### `KeySignature`
- **Purpose**: Defines the tonal center of the piece, determining which notes are naturally sharp or flat.
- **Responsibilities**:
  - Provides a list of notes valid within the key.
  - Can filter notes by octave (e.g., 3rd or 4th octave) to assist with scale drills.
  - Dictates which notes on the staff implicitly require an accidental drawn in the key signature block (the beginning of the staff).

### `TimeSignature`
- **Purpose**: Defines the rhythmic structure (e.g., 4/4, 3/4).
- **Responsibilities**:
  - Determines measure boundaries and beat counts.
  - Helps calculate the X-offset for placing notes horizontally across the staff based on their rhythmic value (whole, half, quarter).

### `Staff`
- **Purpose**: The primary visual container and `displayio.Group` manager for rendering music.
- **Attributes**:
  - `width` & `height` (pixels)
  - `key_signature` (`KeySignature`)
  - `time_signature` (`TimeSignature` - optional/default 4/4)
- **Responsibilities**:
  - **Static Layer**: Draws the 5 horizontal staff lines, treble clef, and key signature accidentals exactly once.
  - **Dynamic Layer**: Handles the placement and visual updating of notes and temporary ledger lines.
  - Calculates proper Y-offsets for notes based on their `ledger_line`.
  - Calculates proper X-offsets for sequential notes based on rhythmic values.

## Vetted Architecture & Performance Considerations

When running on microcontrollers using `displayio`, memory fragmentation and redraw performance are major concerns. The design must accommodate these constraints:

1. **Static vs. Dynamic Grouping**: 
   The `Staff` class should internally use at least two `displayio.Group` objects:
   - `static_group`: Contains the staff lines, clef, time signature, and key signature. This is rendered once and never modified during normal playback.
   - `dynamic_group`: Appended *on top* of the static group. This contains the notes, dynamic accidentals, and temporary ledger lines.

2. **Sprite Sheets (Tilemaps)**:
   Instead of loading individual `.bmp` or `.png` files for every symbol (clef, sharp, flat, whole note, quarter note), we should load a single "sprite sheet" image. A `displayio.TileGrid` can then select the specific tile (e.g., tile index 0 = treble clef, tile index 1 = quarter note). This drastically reduces RAM usage.

3. **Object Pooling for Notes**:
   Dynamically allocating (creating new `TileGrid` objects) and garbage collecting them while a song plays will cause stuttering and memory exhaustion. 
   - The `Staff` should pre-allocate a "pool" of note `TileGrid`s (e.g., 8 or 16 note sprites depending on the screen width and time signature).
   - To display a note, grab an unused sprite from the pool, update its `[x, y]` coordinates, and update its tile index (to change it from a quarter note to a half note, for example).
   - To remove a note, simply move it off-screen (e.g., `y = -1000`) rather than destroying the object.

4. **Dynamic Ledger Lines**:
   If a note is placed above or below the 5 standard lines (e.g., Middle C), the `Staff` must dynamically draw a small horizontal line. These should also be pooled and managed as part of the `dynamic_group`.

## Rendering Pipeline
1. The user instantiates a `Staff` with a `KeySignature` and `TimeSignature`(optional).
2. The `Staff` initializes its `static_group` and draws the background, clef, and key signature.
3. The `Staff` initializes its `dynamic_group` with a pool of hidden note, accidental, and ledger line sprites.
4. The user calls `staff.show_note(note, rhythmic_value)` or `staff.update_sequence(notes)`.
5. The `Staff` activates sprites from the pool, updating their X/Y coordinates based on `note.ledger_line` and rhythmic offsets.
6. Only the bounds of the modified sprites are redrawn by `displayio`, ensuring high performance.

## Testing Strategy
- Use the `display_utils.py` PyGame harness to instantiate fake screens.
- Build visual tests that place notes on a `Staff`, render to PyGame, and optionally output golden `.png` images using `save_to_image()`.
- Verifications can be done headless via pytest (validating that the group contains the correct number of TileGrids) or visually via `show_and_wait()`.
