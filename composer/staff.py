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
        
        self._draw_static_lines()
        self._draw_clef()
        if self.key_signature:
            self._draw_key_signature()

    def _draw_static_lines(self):
        """Draws the 5 standard staff lines."""
        # Using a simple Bitmap/Palette for lines
        line_bitmap = displayio.Bitmap(self.width, 1, 1)
        line_palette = displayio.Palette(1)
        line_palette[0] = self.config.color_data.fg_color # Configurable lines color
        
        for i in range(5):
            y_pos = self.staff_y_start + (i * self.LEDGER_SPACING)
            line_grid = displayio.TileGrid(line_bitmap, pixel_shader=line_palette, x=0, y=y_pos)
            self.static_group.append(line_grid)

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
            clef_grid.x = 3
            
            # Center the clef vertically against the staff lines.
            # The exact Y offset might need to be adjusted depending on the PNG dimensions and whitespace.
            # For now, we'll align the middle of the clef with the middle of the 5 staff lines.
            staff_middle_y = self.staff_y_start + (2 * self.LEDGER_SPACING) + 3
            clef_grid.y = staff_middle_y - (clef_bitmap.height // 2)
            
            self.static_group.append(clef_grid)
        except Exception as e:
            print(f"Warning: Could not load treble clef: {e}")

    def _get_y_for_ledger_line(self, ledger_line):
        """
        Converts a note's ledger_line value into an absolute Y pixel coordinate 
        on the staff.
        """
        steps_down = 4.0 - ledger_line
        # Note: If ledger_line is 4.0 (Top line), steps_down is 0.
        # So we add 0 * 16 = 0, which perfectly lands on staff_y_start.
        # However, a single ledger step (e.g. 4.0 to 3.5, which is line to space)
        # is 0.5. 
        # 0.5 * LEDGER_SPACING(16) = 8 pixels.
        # This matches the distance between a line and an adjacent space!
        return int(self.staff_y_start + (steps_down * self.LEDGER_SPACING))

    def _draw_key_signature(self):
        """
        Draws the accidentals required by the key signature.
        This uses the accidental_sprite_sheet.png and the static_group.
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

            # We know the sprite sheet is 48x48, with 3 sprites side-by-side.
            # So each sprite is 16px wide and 48px tall.
            SPRITE_WIDTH = 16
            SPRITE_HEIGHT = 48
            
            # X offset starts right after the treble clef
            # The treble clef is roughly 25-30px wide + some padding
            current_x = 40
            
            for note in self.key_signature.accidentals:
                # The TileGrid constructor needs the total width/height in tiles, 
                # and the size of each tile in pixels.
                accidental_grid = displayio.TileGrid(
                    accidental_bitmap, 
                    pixel_shader=accidental_palette,
                    width=1, height=1,
                    tile_width=SPRITE_WIDTH, tile_height=SPRITE_HEIGHT
                )
                
                # Let's intercept the ledger_line specifically for the key signature drawing
                # so it draws in the standard spot.
                name_without_octave = note.name.split("_")[0]
                
                if note.accidental == Accidental.SHARP:
                    # Standard Sharp Key Signature Positions
                    pos_map = {
                        "F": 4.0,
                        "C": 2.5,
                        "G": 4.5,
                        "D": 3.0,
                        "A": 1.5,
                        "E": 3.5,
                        "B": 2.0
                    }
                    draw_ledger_line = pos_map.get(name_without_octave, note.ledger_line)
                    
                    accidental_grid[0, 0] = 1
                    visual_center_y = 24
                    
                elif note.accidental == Accidental.FLAT:
                    # Standard Flat Key Signature Positions
                    pos_map = {
                        "B": 2.0,
                        "E": 3.5,
                        "A": 1.5,
                        "D": 3.0,
                        "G": 1.0,
                        "C": 2.5,
                        "F": 0.5
                    }
                    draw_ledger_line = pos_map.get(name_without_octave, note.ledger_line)
                    
                    accidental_grid[0, 0] = 0
                    visual_center_y = 24
                    
                elif note.accidental == Accidental.NATURAL:
                    draw_ledger_line = note.ledger_line
                    accidental_grid[0, 0] = 2
                    visual_center_y = 24
                else:
                    draw_ledger_line = note.ledger_line
                    visual_center_y = 24
                    
                accidental_grid.x = current_x
                
                target_y = self._get_y_for_ledger_line(draw_ledger_line)
                
                # Align visual center of sprite with target y coordinate
                # NOTE: If modifying visual_center_y here does not move the sprite visually,
                # it means displayio is caching/ignoring the fractional update or not redrawing.
                # However, displayio should always redraw if 'y' changes.
                accidental_grid.y = int(target_y - visual_center_y)
                
                self.static_group.append(accidental_grid)
                
                # Move x over for the next accidental
                current_x += SPRITE_WIDTH + 2
                
        except Exception as e:
            print(f"Warning: Could not load accidental sprite sheet: {e}")

    def show_note(self, note, rhythmic_value=None):
        pass

    def update_sequence(self, notes):
        pass