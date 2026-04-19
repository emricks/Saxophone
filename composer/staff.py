import displayio
import adafruit_imageload

from composer.notes import Accidental

class Staff(displayio.Group):
    """
    Represents a musical staff. It is a displayio.Group containing two sub-groups:
    1. static_group: Draws the 5 lines, clef, and key signature (rendered once).
    2. dynamic_group: Contains pooled sprites for notes, accidentals, and ledger lines.
    """

    # Distance between adjacent lines (and also the height of a note body)
    LEDGER_SPACING = 16

    # The staff needs enough vertical room for:
    # - 3 ledger lines above the staff (e.g. high E) + note tail
    # - 5 standard staff lines
    # - 1 ledger line below the staff (e.g. middle C) + note tail
    # Total spaces roughly = 3 above + 4 within + 1 below = 8 spaces
    # Let's give it a comfortable padding of 5 extra spaces total for tails.
    # Total height required: ~13 spaces * LEDGER_SPACING
    HEIGHT = 13 * LEDGER_SPACING

    # --- Accidental sprite sheet layout ---
    # 48 x 48 sheet, three 16-wide columns: [flat, sharp, natural]
    ACC_SPRITE_WIDTH = 14
    ACC_SPRITE_HEIGHT = 42
    ACC_TILE_FLAT = 0
    ACC_TILE_SHARP = 1
    ACC_TILE_NATURAL = 2

    # Vertical offset (in px, from the top of the sprite) of the symbol's
    # "pin point" — i.e. the pixel in the sprite that should land on the
    # target staff line/space.
    # For a sharp, the pin is the intersection of its cross-hairs (center).
    # For a flat, the pin is the center of its round bowl, which sits in the
    # LOWER half of the glyph.
    # For a natural, the pin is the geometric center.
    ACC_PIN_Y = {
        ACC_TILE_SHARP:   21,   # geometric center
        ACC_TILE_FLAT:    30,   # bowl of the flat is below center
        ACC_TILE_NATURAL: 21,
    }

    # Standard Treble-clef positions for key-signature accidentals, expressed
    # as "staff slot" indices:
    #   slot 0  = top line (F5)
    #   slot 1  = space (E5)
    #   slot 2  = line  (D5)
    #   slot 3  = space (C5)
    #   slot 4  = line  (B4)
    #   slot 5  = space (A4)
    #   slot 6  = line  (G4)
    #   slot 7  = space (F4)
    #   slot 8  = line  (E4)
    # i.e. each increment of 1 moves down by LEDGER_SPACING/2 pixels.
    # Negative slots go above the top line.
    SHARP_SLOTS = {
        "F": 0,   # F on top line
        "C": 3,   # C in third space
        "G": -1,  # G above the top line
        "D": 2,   # D on fourth line (from top)
        "A": 5,   # A in second space (from top)
        "E": 1,   # E in top space
        "B": 4,   # B on middle line
    }
    FLAT_SLOTS = {
        "B": 4,   # B on middle line
        "E": 1,   # E in top space
        "A": 5,   # A in second space
        "D": 2,   # D on fourth line (from top)
        "G": 6,   # G on second line (from top)
        "C": 3,   # C in third space
        "F": 7,   # F in bottom space
    }

    def __init__(self, width, config, key_signature=None, time_signature=None):
        super().__init__()
        self.width = width
        self.height = self.HEIGHT
        self.config = config
        self.key_signature = key_signature
        self.time_signature = time_signature

        # Two main layers
        self.static_group = displayio.Group()
        self.dynamic_group = displayio.Group()

        self.append(self.static_group)
        self.append(self.dynamic_group)

        # The topmost line of the standard 5 lines.
        # If we need room for 3 ledger lines above, the top staff line starts
        # at roughly 4 * LEDGER_SPACING pixels down from the top of the group.
        self.staff_y_start = 4 * self.LEDGER_SPACING

        # Remember the exact Y pixel of each of the 5 staff lines as we draw
        # them, so consumers (e.g. key-signature drawing) never have to
        # recompute them.
        # Index 0 = top line (F5), index 4 = bottom line (E4).
        self.staff_line_ys = []

        self._draw_static_lines()
        self._draw_clef()
        if self.key_signature:
            self._draw_key_signature()

    def _draw_static_lines(self):
        """Draws the 5 standard staff lines."""
        # Using a simple Bitmap/Palette for lines
        line_bitmap = displayio.Bitmap(self.width, 1, 1)
        line_palette = displayio.Palette(1)
        line_palette[0] = self.config.color_data.fg_color  # Configurable lines color

        self.staff_line_ys = []
        for i in range(5):
            y_pos = self.staff_y_start + (i * self.LEDGER_SPACING)
            self.staff_line_ys.append(y_pos)
            line_grid = displayio.TileGrid(line_bitmap, pixel_shader=line_palette, x=0, y=y_pos)
            self.static_group.append(line_grid)

    def _y_for_slot(self, slot):
        """
        Returns the absolute Y pixel of a staff "slot", where:
          slot 0  = top line,
          slot 1  = space below top line,
          slot 2  = next line down,
          ...
          slot 8  = bottom line.
        Fractional/negative slots are allowed and extrapolate linearly.
        """
        top_y = self.staff_line_ys[0]
        return int(top_y + slot * (self.LEDGER_SPACING / 2))

    def _draw_clef(self):
        """Draws the treble clef at the start of the staff."""
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

            # Give it a tiny bit of left padding
            clef_grid.x = 0

            # Center the clef vertically against the staff lines.
            staff_middle_y = self.staff_y_start + (2 * self.LEDGER_SPACING) + 3
            clef_grid.y = staff_middle_y - (clef_bitmap.height // 2)

            self.static_group.append(clef_grid)
        except Exception as e:
            print(f"Warning: Could not load treble clef: {e}")

    def _get_y_for_ledger_line(self, ledger_line):
        """
        Converts a note's ledger_line value into an absolute Y pixel coordinate
        on the staff. Used for placing notes in the dynamic layer.
        """
        steps_down = 4.0 - ledger_line
        return int(self.staff_y_start + (steps_down * self.LEDGER_SPACING))

    def _draw_key_signature(self):
        """
        Draws the accidentals required by the key signature into the static
        layer. Each accidental is pinned directly to a known staff-line / space
        Y-coordinate that we recorded when the lines were drawn — no
        round-tripping through note ledger_line values.
        """
        try:
            accidental_bitmap, accidental_palette = adafruit_imageload.load(
                "data/img/accidental_sprite_sheet.png",
                bitmap=displayio.Bitmap,
                palette=displayio.Palette
            )

            # Make sure we set the background transparent and the lines to fg_color
            if len(accidental_palette) > 1:
                accidental_palette.make_transparent(1)
                accidental_palette[0] = self.config.color_data.fg_color

            # X offset starts right after the treble clef
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
                    slot = None  # fall back to note ledger_line
                else:
                    continue  # nothing to draw

                # Determine target Y: prefer the canonical key-signature slot;
                # if unknown, fall back to the note's actual ledger position.
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

    def show_note(self, note, rhythmic_value=None):
        pass

    def update_sequence(self, notes):
        pass