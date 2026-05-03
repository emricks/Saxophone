import math
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
    ACC_SPRITE_WIDTH = 14
    ACC_SPRITE_HEIGHT = 42
    ACC_TILE_FLAT = 0
    ACC_TILE_SHARP = 1
    ACC_TILE_NATURAL = 2

    ACC_PIN_Y = {
        ACC_TILE_SHARP:   21,
        ACC_TILE_FLAT:    30,
        ACC_TILE_NATURAL: 21,
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

    # --- Note sprite sheet layout (150x96, 30x48 tiles) ---
    # Top row: eighth(0), quarter(1), half(2), whole(3)
    # Bottom row: eighth rest(5), quarter rest(6), half rest(7), whole rest(8)
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
        Duration.EIGHTH:  5,
        Duration.QUARTER: 6,
        Duration.HALF:    7,
        Duration.WHOLE:   8,
    }
    # Pixel within the rest sprite that should land on REST_LEDGER_LINE.
    REST_PIN_Y = 24
    # Rests render centered on the middle staff line.
    REST_LEDGER_LINE = 2.0

    LEDGER_LINE_WIDTH = 26  # pixels wide for extra ledger lines
    NOTE_POOL_SIZE = 8

    # Horizontal spacing: quarter note = 1 beat = BEAT_WIDTH pixels
    BEAT_WIDTH = 30
    DURATION_BEATS = {
        Duration.WHOLE:   4,
        Duration.HALF:    2,
        Duration.QUARTER: 1,
        Duration.EIGHTH:  1,  # give eighth same column width as quarter for readability
    }

    def __init__(self, width: int, config: Config, key_signature: KeySignature = KeySignatures.C_MAJOR, time_signature: None = None) -> None:
        super().__init__()
        self.width = width
        self.height = self.HEIGHT
        self.config = config
        self.key_signature = key_signature
        self.time_signature = time_signature

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
        self._note_pool_next = 0
        self._acc_pool_next = 0
        self._ledger_pool_next = 0

        self._draw_static_lines()
        self._draw_clef()
        if self.key_signature:
            self._draw_key_signature()
        self._init_dynamic_pool()

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
                current_x += self.ACC_SPRITE_WIDTH

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

    def update_sequence(self, items) -> None:
        """
        Renders a list of TimedNote / Rest objects onto the dynamic layer of the staff.
        Items are centered within their beat-proportional horizontal slots so that,
        for example, a whole note sits in the middle of the measure rather than the
        far-left edge.  Assumes 4/4 time (4 beats per measure).
        """
        for tg in self._note_pool:
            tg.x = -1000
        for tg in self._acc_pool:
            tg.x = -1000
        for tg in self._ledger_pool:
            tg.x = -1000

        self._note_pool_next = 0
        self._acc_pool_next = 0
        self._ledger_pool_next = 0

        num_ks_acc = len(self.key_signature.accidentals) if self.key_signature else 0
        content_x = 32 + (num_ks_acc * self.ACC_SPRITE_WIDTH) + 8
        available_w = self.width - content_x - 4
        beats_per_measure = 4
        beat_w = available_w / beats_per_measure

        current_beat = 0

        for item in items:
            duration = item.duration
            beats = self.DURATION_BEATS.get(duration, 1)
            slot_cx = int(content_x + (current_beat + beats / 2.0) * beat_w)

            if isinstance(item, Rest):
                self._draw_rest(item, slot_cx)
            else:
                self._draw_timed_note(item, slot_cx)

            current_beat += beats

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

        if self._note_pool_next < len(self._note_pool):
            note_tg = self._note_pool[self._note_pool_next]
            note_tg[0, 0] = self.NOTE_TILE.get(duration, 1)
            note_tg.x = slot_cx - pin_x
            note_tg.y = note_y - self.NOTE_PIN_Y.get(duration, 42)
            self._note_pool_next += 1

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