import displayio

class Staff(displayio.Group):
    """
    Represents a musical staff. It is a displayio.Group containing two sub-groups:
    1. static_group: Draws the 5 lines, clef, and key signature (rendered once).
    2. dynamic_group: Contains pooled sprites for notes, accidentals, and ledger lines.
    """
    
    # Distance between adjacent lines (and also the height of a note body)
    LEDGER_SPACING = 10
    
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

    def show_note(self, note, rhythmic_value=None):
        """
        Displays a note on the staff. 
        Currently a stub to be built out with object pooling and dynamic rendering.
        """
        pass

    def update_sequence(self, notes):
        """
        Displays a sequence of notes.
        Currently a stub.
        """
        pass
