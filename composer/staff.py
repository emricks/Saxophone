import math
import bitmaptools
import displayio
import adafruit_imageload

from composer.key_signature import KeySignature, KeySignatures
from composer.notes import Accidental, Duration, Note, Rest, TimedNote
from data.config import Config

class Staff(displayio.Group):
    """
    Represents a musical staff. It is a displayio.Group containing two sub-groups:
    1. static_group: Draws the 5 lines, clef, and key signature (rendered once).
    2. dynamic_group: Contains pooled sprites for notes, accidentals, and ledger lines.
    """

    LEDGER_SPACING = 16
    HEIGHT = 13 * LEDGER_SPACING

    # --- Accidental sprite sheet layout ---
    ACC_SPRITE_WIDTH = 12
    ACC_SPRITE_HEIGHT = 36
    # Horizontal step between key-signature accidentals. Smaller than
    # ACC_SPRITE_WIDTH because the sprites have transparent padding on each
    # side — overlap is invisible and buys back staff width for notes.
    ACC_KEY_STRIDE = 9
    ACC_TILE_FLAT = 0
    ACC_TILE_SHARP = 1
    ACC_TILE_NATURAL = 2

    ACC_PIN_Y = {
        ACC_TILE_SHARP:   18,
        ACC_TILE_FLAT:    26,
        ACC_TILE_NATURAL: 18,
    }

    SHARP_SLOTS = {
        "F": 0,
        "C": 3,
        "G": -1,
        "D": 2,
        "A": 5,
        "E": 1,
        "B": 4,
    }
    FLAT_SLOTS = {
        "B": 4,
        "E": 1,
        "A": 5,
        "D": 2,
        "G": 6,
        "C": 3,
        "F": 7,
    }

    # --- Note sprite sheet layout (120x96, 30x48 tiles, 4 cols x 2 rows) ---
    # Top row:    eighth(0), quarter(1), half(2), whole(3)
    # Bottom row: eighth rest(4), quarter rest(5), half rest(6), whole rest(7)
    NOTE_SHEET_PATH = "data/img/note_sprite_sheet.png"
    NOTE_SPRITE_WIDTH = 30
    NOTE_SPRITE_HEIGHT = 48

    NOTE_TILE = {
        Duration.EIGHTH:  0,
        Duration.QUARTER: 1,
        Duration.HALF:    2,
        Duration.WHOLE:   3,
    }

    # Pixel within the sprite that should land on the note's staff Y position.
    # Stemmed notes have the head near the sprite bottom; whole note is centered.
    NOTE_PIN_Y = {
        Duration.EIGHTH:  40,
        Duration.QUARTER: 40,
        Duration.HALF:    40,
        Duration.WHOLE:   40,
    }
    NOTE_PIN_X = {
        Duration.EIGHTH:  8,
        Duration.QUARTER: 8,
        Duration.HALF:    8,
        Duration.WHOLE:   8,
    }

    REST_TILE = {
        Duration.EIGHTH:  4,
        Duration.QUARTER: 5,
        Duration.HALF:    6,
        Duration.WHOLE:   7,
    }
    # Pixel within the rest sprite that should land on REST_LEDGER_LINE.
    REST_PIN_Y = 24
    # Rests render centered on the middle staff line.
    REST_LEDGER_LINE = 2.0

    LEDGER_LINE_WIDTH = 26  # pixels wide for extra ledger lines
    NOTE_POOL_SIZE = 8

    # Horizontal layout weights (column pixel widths) per duration. Sub-linear
    # in musical beats so a sparse measure (e.g. one whole note) doesn't gobble
    # the entire staff — the remaining width previews upcoming items from the
    # next measure(s). Eighth shares quarter width for readability; otherwise
    # weights grow but at a discount versus their musical-beat count.
    # Tune in concert with test/staff_layout_test.py.
    LAYOUT_WEIGHT = {
        Duration.EIGHTH:  32,
        Duration.QUARTER: 32,
        Duration.HALF:    44,
        Duration.WHOLE:   60,
    }
    BEATS_PER_MEASURE = 4

    def __init__(self, width: int, config: Config, key_signature: KeySignature = KeySignatures.C_MAJOR, time_signature: None = None, enable_progress: bool = False) -> None:
        super().__init__()
        self.width = width
        self.height = self.HEIGHT
        self.config = config
        self.key_signature = key_signature
        self.time_signature = time_signature
        self.enable_progress = enable_progress

        self.static_group = displayio.Group()
        self.dynamic_group = displayio.Group()

        self.append(self.static_group)
        self.append(self.dynamic_group)

        self.staff_y_start = 4 * self.LEDGER_SPACING
        self.staff_line_ys = []

        # Pool state
        self._note_pool = []
        self._acc_pool = []
        self._ledger_pool = []
        self._measure_line_pool = []
        self._note_pool_next = 0
        self._acc_pool_next = 0
        self._ledger_pool_next = 0
        self._measure_line_pool_next = 0

        # Progress-overlay state. Allocated only when enable_progress=True;
        # otherwise these stay None and Staff behaves exactly as before.
        self._note_bitmap_source = None
        self._progress_overlay_bitmap = None
        self._progress_overlay_tilegrid = None
        self._progress_tile_cache = None
        self._progress_current_tile = None
        self._progress_hide_top = -1
        # Topmost non-transparent row in the current tile's silhouette. Fill
        # ramps from H up to this row (not 0) so a whole note — which only
        # occupies the bottom third of the tile — doesn't appear "full" at
        # ~33% fraction.
        self._progress_glyph_top = 0

        self._draw_static_lines()
        self._draw_clef()
        if self.key_signature:
            self._draw_key_signature()
        self._init_dynamic_pool()
        if self.enable_progress:
            self._init_progress_overlay()

    def _draw_static_lines(self) -> None:
        line_bitmap = displayio.Bitmap(self.width, 1, 1)
        line_palette = displayio.Palette(1)
        line_palette[0] = self.config.color_data.fg_color

        self.staff_line_ys = []
        for i in range(5):
            y_pos = self.staff_y_start + (i * self.LEDGER_SPACING)
            self.staff_line_ys.append(y_pos)
            line_grid = displayio.TileGrid(line_bitmap, pixel_shader=line_palette, x=0, y=y_pos)
            self.static_group.append(line_grid)

    def _y_for_slot(self, slot: float) -> int:
        top_y = self.staff_line_ys[0]
        return int(top_y + slot * (self.LEDGER_SPACING / 2))

    def _draw_clef(self) -> None:
        try:
            clef_bitmap, clef_palette = adafruit_imageload.load(
                "data/img/treble_clef_white.png",
                bitmap=displayio.Bitmap,
                palette=displayio.Palette
            )

            if len(clef_palette) > 1:
                clef_palette.make_transparent(1)
                clef_palette[0] = self.config.color_data.fg_color

            clef_grid = displayio.TileGrid(clef_bitmap, pixel_shader=clef_palette)
            clef_grid.x = 0
            staff_middle_y = self.staff_y_start + (2 * self.LEDGER_SPACING) + 3
            clef_grid.y = staff_middle_y - (clef_bitmap.height // 2)

            self.static_group.append(clef_grid)
        except Exception as e:
            print(f"Warning: Could not load treble clef: {e}")

    def _get_y_for_ledger_line(self, ledger_line: float) -> int:
        steps_down = 4.0 - ledger_line
        return int(self.staff_y_start + (steps_down * self.LEDGER_SPACING))

    def _draw_key_signature(self) -> None:
        try:
            accidental_bitmap, accidental_palette = adafruit_imageload.load(
                "data/img/accidental_sprite_sheet.png",
                bitmap=displayio.Bitmap,
                palette=displayio.Palette
            )

            if len(accidental_palette) > 1:
                accidental_palette.make_transparent(1)
                accidental_palette[0] = self.config.color_data.fg_color

            current_x = 32

            for note in self.key_signature.accidentals:
                name_without_octave = note.name.split("_")[0]

                if note.accidental == Accidental.SHARP:
                    tile_index = self.ACC_TILE_SHARP
                    slot = self.SHARP_SLOTS.get(name_without_octave)
                elif note.accidental == Accidental.FLAT:
                    tile_index = self.ACC_TILE_FLAT
                    slot = self.FLAT_SLOTS.get(name_without_octave)
                elif note.accidental == Accidental.NATURAL:
                    tile_index = self.ACC_TILE_NATURAL
                    slot = None
                else:
                    continue

                if slot is not None:
                    target_y = self._y_for_slot(slot)
                else:
                    target_y = self._get_y_for_ledger_line(note.ledger_line)

                pin_y = self.ACC_PIN_Y[tile_index]

                accidental_grid = displayio.TileGrid(
                    accidental_bitmap,
                    pixel_shader=accidental_palette,
                    width=1, height=1,
                    tile_width=self.ACC_SPRITE_WIDTH,
                    tile_height=self.ACC_SPRITE_HEIGHT,
                )
                accidental_grid[0, 0] = tile_index
                accidental_grid.x = current_x
                accidental_grid.y = target_y - pin_y

                self.static_group.append(accidental_grid)
                current_x += self.ACC_KEY_STRIDE

        except Exception as e:
            print(f"Warning: Could not load accidental sprite sheet: {e}")

    def _init_dynamic_pool(self) -> None:
        """Pre-allocates pooled sprites for notes, accidentals, and ledger lines."""
        try:
            note_bitmap, note_palette = adafruit_imageload.load(
                self.NOTE_SHEET_PATH,
                bitmap=displayio.Bitmap,
                palette=displayio.Palette,
            )
            if len(note_palette) > 1:
                note_palette.make_transparent(1)
                note_palette[0] = self.config.color_data.fg_color

            # Retain a reference so the progress overlay can use this bitmap
            # as a pristine source (it's never mutated by the pool path).
            self._note_bitmap_source = note_bitmap

            for _ in range(self.NOTE_POOL_SIZE):
                tg = displayio.TileGrid(
                    note_bitmap,
                    pixel_shader=note_palette,
                    width=1, height=1,
                    tile_width=self.NOTE_SPRITE_WIDTH,
                    tile_height=self.NOTE_SPRITE_HEIGHT,
                )
                tg.x = -1000
                tg.y = -1000
                self._note_pool.append(tg)
                self.dynamic_group.append(tg)
        except Exception as e:
            print(f"Warning: Could not load note sprite sheet: {e}")

        try:
            acc_bitmap, acc_palette = adafruit_imageload.load(
                "data/img/accidental_sprite_sheet.png",
                bitmap=displayio.Bitmap,
                palette=displayio.Palette,
            )
            if len(acc_palette) > 1:
                acc_palette.make_transparent(1)
                acc_palette[0] = self.config.color_data.fg_color

            for _ in range(self.NOTE_POOL_SIZE):
                tg = displayio.TileGrid(
                    acc_bitmap,
                    pixel_shader=acc_palette,
                    width=1, height=1,
                    tile_width=self.ACC_SPRITE_WIDTH,
                    tile_height=self.ACC_SPRITE_HEIGHT,
                )
                tg.x = -1000
                tg.y = -1000
                self._acc_pool.append(tg)
                self.dynamic_group.append(tg)
        except Exception as e:
            print(f"Warning: Could not load accidental sprite sheet for dynamic pool: {e}")

        ledger_bitmap = displayio.Bitmap(self.LEDGER_LINE_WIDTH, 1, 1)
        ledger_palette = displayio.Palette(1)
        ledger_palette[0] = self.config.color_data.fg_color
        for _ in range(self.NOTE_POOL_SIZE * 3):
            tg = displayio.TileGrid(ledger_bitmap, pixel_shader=ledger_palette)
            tg.x = -1000
            tg.y = -1000
            self._ledger_pool.append(tg)
            self.dynamic_group.append(tg)

        # Measure-line pool — vertical lines drawn at 4-beat boundaries within
        # the layout. Sized to span exactly the 5-line staff (top of line 0
        # through bottom of line 4 inclusive). Lives in static_group alongside
        # the staff lines: same z-layer (measure lines render behind notes,
        # matching music-notation convention), and on overlay staves whose
        # static_group is popped (drill_staff in ScaleDrillState) these get
        # cleared out the same way the staff lines do — so measure lines only
        # ever exist on the staff that draws the actual lines.
        measure_line_height = 4 * self.LEDGER_SPACING + 1
        measure_bitmap = displayio.Bitmap(1, measure_line_height, 1)
        measure_palette = displayio.Palette(1)
        measure_palette[0] = self.config.color_data.fg_color
        for _ in range(4):  # 4 verticals is plenty for any reasonable window
            tg = displayio.TileGrid(measure_bitmap, pixel_shader=measure_palette)
            tg.x = -1000
            tg.y = -1000
            self._measure_line_pool.append(tg)
            self.static_group.append(tg)

    def _init_progress_overlay(self) -> None:
        """Allocates two 30x48 bitmaps for progressive note fill:
        - overlay: the on-screen target. Mutated incrementally — never wholesale
          rebuilt — so there is no intermediate 'fully filled' frame that displayio's
          auto-refresh could catch as a flash.
        - tile_cache: holds the current note's silhouette so set_progress can copy
          newly-revealed rows out of it without sub-region blits from the multi-tile
          spritesheet."""
        if self._note_bitmap_source is None:
            return

        W, H = self.NOTE_SPRITE_WIDTH, self.NOTE_SPRITE_HEIGHT

        self._progress_overlay_bitmap = displayio.Bitmap(W, H, 2)
        self._progress_tile_cache = displayio.Bitmap(W, H, 2)

        bitmaptools.fill_region(self._progress_overlay_bitmap, 0, 0, W, H, 1)
        bitmaptools.fill_region(self._progress_tile_cache,     0, 0, W, H, 1)

        overlay_palette = displayio.Palette(2)
        overlay_palette[0] = self.config.color_data.fingering_color
        overlay_palette.make_transparent(1)

        self._progress_overlay_tilegrid = displayio.TileGrid(
            self._progress_overlay_bitmap,
            pixel_shader=overlay_palette,
        )
        self._progress_overlay_tilegrid.x = -1000
        self._progress_overlay_tilegrid.y = -1000
        self.dynamic_group.append(self._progress_overlay_tilegrid)

    def _load_tile_into_cache(self, tile_index: int) -> None:
        """Copies one 30x48 tile from the multi-tile spritesheet into the tile_cache
        via direct pixel access (avoids sub-region blit). Runs once per note advance.
        Also records the topmost row containing any ink (palette index 0) so the
        fill range can be scoped to the glyph extent — a whole note's oval lives
        in the bottom of the tile and shouldn't be "full" before the reveal
        reaches it."""
        if self._progress_tile_cache is None or self._note_bitmap_source is None:
            return
        W, H = self.NOTE_SPRITE_WIDTH, self.NOTE_SPRITE_HEIGHT
        cols = self._note_bitmap_source.width // W
        src_x = (tile_index % cols) * W
        src_y = (tile_index // cols) * H
        src = self._note_bitmap_source
        dst = self._progress_tile_cache
        glyph_top = H  # default = empty tile
        for y in range(H):
            sy = src_y + y
            row_has_ink = False
            for x in range(W):
                v = src[src_x + x, sy]
                dst[x, y] = v
                if v == 0 and not row_has_ink:
                    row_has_ink = True
            if row_has_ink and glyph_top == H:
                glyph_top = y
        self._progress_glyph_top = glyph_top

    def _ledger_lines_for_note(self, ledger_line: float) -> list[int]:
        """Returns ledger_line positions (integers) that must be drawn for this note."""
        positions = []
        if ledger_line < 0:
            # Lines from -1 down to ceil(ledger_line), e.g. C4(-1.0) → [-1], B3(-1.5) → [-1]
            stop = math.ceil(ledger_line)
            for i in range(-1, stop - 1, -1):
                positions.append(i)
        elif ledger_line > 4:
            # Lines from 5 up to floor(ledger_line), e.g. A5(5.0) → [5], C6(6.0) → [5,6]
            stop = int(math.floor(ledger_line))
            for i in range(5, stop + 1):
                positions.append(i)
        return positions

    def _needs_accidental(self, note: Note) -> str | None:
        """
        Returns the Accidental type to draw alongside this note, or None if none is needed.
        Compares the note's accidental against the key signature to avoid redundant markings.
        """
        if not self.key_signature:
            return note.accidental

        base_name = note.name.split("_")[0]

        ks_accidental = None
        for ks_note in self.key_signature.accidentals:
            if ks_note.name.split("_")[0] == base_name:
                ks_accidental = ks_note.accidental
                break

        if ks_accidental == note.accidental:
            return None
        if ks_accidental is not None and note.accidental is None:
            return Accidental.NATURAL
        return note.accidental

    def _layout(self, items):
        """Greedy left-to-right packing of items into the staff's note area.

        Returns (center_xs, right_edges, cum_beats) as parallel lists, one
        entry per item that fit. Items whose column would overrun the staff
        edge are dropped silently — callers can pass an oversized lookahead
        window. Pool size is also a cap.

        cum_beats holds running musical-beat totals at each item's right edge,
        used by set_measure_lines to place barlines at musical boundaries
        (not visual ones) regardless of how widths were compressed.
        """
        num_ks_acc = len(self.key_signature.accidentals) if self.key_signature else 0
        content_x = 32 + (num_ks_acc * self.ACC_KEY_STRIDE) + 8
        right_edge_limit = self.width - 4

        center_xs = []
        right_edges = []
        cum_beats = []

        cursor_x = content_x
        cursor_beats = 0.0
        for item in items:
            if len(center_xs) >= self.NOTE_POOL_SIZE:
                break
            weight = self.LAYOUT_WEIGHT.get(item.duration, self.LAYOUT_WEIGHT[Duration.QUARTER])
            slot_right = cursor_x + weight
            if slot_right > right_edge_limit:
                break
            center_xs.append(int(cursor_x + weight / 2.0))
            right_edges.append(int(slot_right))
            cursor_beats += Duration.BEATS.get(item.duration, 1.0)
            cum_beats.append(cursor_beats)
            cursor_x = slot_right

        return center_xs, right_edges, cum_beats

    def update_sequence(self, items) -> None:
        """Renders a list of TimedNote / Rest objects onto the dynamic layer
        of the staff. Items are sized by LAYOUT_WEIGHT (sub-linear in musical
        beats) and packed left-to-right; items beyond the staff edge are
        dropped silently.

        Measure lines are not drawn here — call `set_measure_lines` separately,
        on whichever staff should own them.
        """
        for tg in self._note_pool:
            tg.x = -1000
        for tg in self._acc_pool:
            tg.x = -1000
        for tg in self._ledger_pool:
            tg.x = -1000

        if self.enable_progress and self._progress_overlay_tilegrid is not None:
            self._progress_overlay_tilegrid.x = -1000
            self._progress_overlay_tilegrid.y = -1000
            self._progress_current_tile = None
            self._progress_hide_top = -1

        self._note_pool_next = 0
        self._acc_pool_next = 0
        self._ledger_pool_next = 0

        center_xs, _, _ = self._layout(items)
        for item, slot_cx in zip(items, center_xs):
            if isinstance(item, Rest):
                self._draw_rest(item, slot_cx)
            else:
                self._draw_timed_note(item, slot_cx)

    def set_measure_lines(self, items, start_beat: float = 0) -> None:
        """Places measure lines at musical-beat boundaries that fall on item
        edges within the laid-out window. Uses the same layout as
        update_sequence so lines and notes always agree.

        Lives in static_group so the lines render behind notes and share the
        owning staff's fg_color (the overlay pattern in scale_drill_state
        draws notes on a recolored staff and lines on the base staff)."""
        for tg in self._measure_line_pool:
            tg.x = -1000
        self._measure_line_pool_next = 0

        _, right_edges, cum_beats = self._layout(items)
        if not right_edges:
            return

        pool_n = 0
        # Skip the very last edge — it sits at the staff's right margin and
        # would visually merge with the fingering chart.
        for i in range(len(right_edges) - 1):
            if pool_n >= len(self._measure_line_pool):
                break
            global_beat = start_beat + cum_beats[i]
            ratio = global_beat / self.BEATS_PER_MEASURE
            # Tolerate float rounding from eighth-note sums.
            if ratio > 0 and abs(ratio - round(ratio)) < 1e-6:
                line_tg = self._measure_line_pool[pool_n]
                line_tg.x = right_edges[i]
                line_tg.y = self.staff_y_start
                pool_n += 1
        self._measure_line_pool_next = pool_n

    def _draw_timed_note(self, timed_note: TimedNote, slot_cx: int) -> None:
        note = timed_note.note
        duration = timed_note.duration
        note_y = self._get_y_for_ledger_line(note.ledger_line)
        pin_x = self.NOTE_PIN_X.get(duration, 8)

        for ll_pos in self._ledger_lines_for_note(note.ledger_line):
            if self._ledger_pool_next < len(self._ledger_pool):
                ll_tg = self._ledger_pool[self._ledger_pool_next]
                ll_tg.x = slot_cx - self.LEDGER_LINE_WIDTH // 2
                ll_tg.y = self._get_y_for_ledger_line(ll_pos)
                self._ledger_pool_next += 1

        acc_type = self._needs_accidental(note)
        if acc_type and self._acc_pool_next < len(self._acc_pool):
            if acc_type == Accidental.SHARP:
                tile_index = self.ACC_TILE_SHARP
            elif acc_type == Accidental.FLAT:
                tile_index = self.ACC_TILE_FLAT
            else:
                tile_index = self.ACC_TILE_NATURAL
            acc_tg = self._acc_pool[self._acc_pool_next]
            acc_tg[0, 0] = tile_index
            acc_tg.x = slot_cx - pin_x - self.ACC_SPRITE_WIDTH - 2
            acc_tg.y = note_y - self.ACC_PIN_Y[tile_index]
            self._acc_pool_next += 1

        # Always draw the silhouette from the pool so the played note is visible
        # regardless of fill state (wrong notes need to appear too).
        if self._note_pool_next < len(self._note_pool):
            note_tg = self._note_pool[self._note_pool_next]
            note_tg[0, 0] = self.NOTE_TILE.get(duration, 1)
            note_tg.x = slot_cx - pin_x
            note_tg.y = note_y - self.NOTE_PIN_Y.get(duration, 42)
            self._note_pool_next += 1

        # When progress is enabled, layer the fill overlay on top of the pool silhouette.
        # The overlay sits at the same position; its bottom-up reveal paints in a
        # contrasting color over the pool's silhouette as the user holds.
        if self.enable_progress and self._progress_overlay_tilegrid is not None:
            pin_y = self.NOTE_PIN_Y.get(duration, 42)
            self._progress_overlay_tilegrid.x = slot_cx - pin_x
            self._progress_overlay_tilegrid.y = note_y - pin_y
            tile_index = self.NOTE_TILE.get(duration, 1)
            self._progress_current_tile = tile_index
            # Cache this note's silhouette so set_progress() can copy newly-revealed
            # rows out of it (full-source coords, no sub-region blits required).
            self._load_tile_into_cache(tile_index)
            # Reset overlay to fully transparent so the starting state matches the
            # tracked hide_top (= H, fully hidden).
            bitmaptools.fill_region(
                self._progress_overlay_bitmap,
                0, 0, self.NOTE_SPRITE_WIDTH, self.NOTE_SPRITE_HEIGHT,
                1,
            )
            self._progress_hide_top = self.NOTE_SPRITE_HEIGHT

    def set_progress(self, fraction: float) -> None:
        """Renders a bottom-up fill (0.0–1.0) of the currently-shown note's silhouette
        into the dedicated overlay.

        Mutates only the rows that crossed a pixel boundary since the last call,
        so the overlay never holds an intermediate 'fully filled' state that
        displayio's auto-refresh could catch as a flash.

        No-op if enable_progress=False or no current note."""
        if not self.enable_progress or self._progress_overlay_bitmap is None:
            return
        if self._progress_current_tile is None or self._progress_tile_cache is None:
            return

        if fraction < 0.0:
            fraction = 0.0
        elif fraction > 1.0:
            fraction = 1.0
        H = self.NOTE_SPRITE_HEIGHT
        W = self.NOTE_SPRITE_WIDTH
        # Fill ramps over the glyph's actual vertical extent, not the full
        # tile. fraction=1.0 reveals down to glyph_top; anything above that
        # row is transparent in the silhouette anyway.
        glyph_top = self._progress_glyph_top
        fill_range = H - glyph_top
        hide_top = H - int(fraction * fill_range)

        prev = self._progress_hide_top
        if hide_top == prev:
            return
        self._progress_hide_top = hide_top

        overlay = self._progress_overlay_bitmap
        cache = self._progress_tile_cache

        if hide_top < prev:
            # Fill grew: reveal rows [hide_top, prev) by copying from the silhouette cache.
            # Manual pixel copy keeps source/dest coords aligned without a sub-region blit.
            for y in range(hide_top, prev):
                for x in range(W):
                    overlay[x, y] = cache[x, y]
        else:
            # Fill shrank: hide rows [prev, hide_top) by stamping the transparent index.
            bitmaptools.fill_region(overlay, 0, prev, W, hide_top, 1)

    def _draw_rest(self, rest: Rest, slot_cx: int) -> None:
        if self._note_pool_next >= len(self._note_pool):
            return
        rest_y = self._get_y_for_ledger_line(self.REST_LEDGER_LINE)
        pin_x = self.NOTE_PIN_X.get(rest.duration, 8)
        rest_tg = self._note_pool[self._note_pool_next]
        rest_tg[0, 0] = self.REST_TILE.get(rest.duration, self.REST_TILE[Duration.QUARTER])
        rest_tg.x = slot_cx - pin_x
        rest_tg.y = rest_y - self.REST_PIN_Y
        self._note_pool_next += 1

    def show_note(self, note: Note, duration: str = Duration.QUARTER) -> None:
        """Renders a single note on the staff. Convenience wrapper around update_sequence."""
        self.update_sequence([TimedNote(note, duration)])