try:
    import board
except ModuleNotFoundError:
    # If the platform does not fully support circuitpython's board 
    # module (e.g. running in standard CPython on macOS for tests),
    # fake it so imports don't crash.
    class FakeBoard:
        D11 = "D11"
        # Add any other board pins used directly
    board = FakeBoard()

class ButtonHardwareSource:
    ONBOARD = "ONBOARD"
    MCP1 = "MCP1"
    MCP2 = "MCP2"

class BoundingBox:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
    def calculate_width(self):
        return self.x1 - self.x0
    def calculate_height(self):
        return self.y1 - self.y0

class ButtonDef:
    # Use an auto-incrementing class variable to assign unique bits
    _next_fingering_bit = 0

    def __init__(self, hw_source, hw_pin, bounding_box: BoundingBox = None, is_fingering=True):
        self.hw_source = hw_source  # e.g., 'ONBOARD' or 'MCP'
        self.hw_pin = hw_pin  # board.D11 or MCP pin integer (0, 1, etc.)
        
        if is_fingering:
            # Automatically assign the next available unique bit for this button
            self.fingering_bit = ButtonDef._next_fingering_bit
            ButtonDef._next_fingering_bit += 1
        else:
            self.fingering_bit = None
        
        self.is_pressed = False
        self.was_pressed = False
        self.bounding_box = bounding_box

    @property
    def just_pressed(self):
        """Returns True only on the frame the button was initially pressed."""
        return self.is_pressed and not self.was_pressed

    @property
    def just_released(self):
        """Returns True only on the frame the button was released."""
        return not self.is_pressed and self.was_pressed

class Buttons:
    # official key names

    # Right hand
    R_F_SHARP = ButtonDef(ButtonHardwareSource.MCP1, 4, bounding_box=BoundingBox(15, 176, 36, 186))
    R_HIGH_F_SHARP = ButtonDef(ButtonHardwareSource.MCP1, 0, bounding_box=BoundingBox(21, 145, 33, 170))
    R_C = ButtonDef(ButtonHardwareSource.MCP1, 7, bounding_box=BoundingBox(7, 124, 18, 136))
    R_E = ButtonDef(ButtonHardwareSource.MCP1, 9, bounding_box=BoundingBox(7, 106, 18, 119))
    R_1 = ButtonDef(ButtonHardwareSource.MCP1, 6, bounding_box=BoundingBox(40, 129, 60, 149))
    R_2 = ButtonDef(ButtonHardwareSource.MCP1, 8, bounding_box=BoundingBox(40, 158, 60, 178))
    R_3 = ButtonDef(ButtonHardwareSource.MCP1, 1, bounding_box=BoundingBox(40, 188, 60, 207))
    R_B_FLAT = ButtonDef(ButtonHardwareSource.MCP1, 5, bounding_box=BoundingBox(7, 141, 18, 158))
    R_LOW_E_FLAT = ButtonDef(ButtonHardwareSource.MCP1, 3, bounding_box=BoundingBox(2, 199, 30, 215))
    R_LOW_C = ButtonDef(ButtonHardwareSource.MCP1, 2, bounding_box=BoundingBox(2, 220, 32, 238))

    # Left hand
    L_OCTAVE = ButtonDef(ButtonHardwareSource.MCP2, 6, bounding_box=BoundingBox(9, 25, 27, 46))
    L_1 = ButtonDef(ButtonHardwareSource.MCP2, 10, bounding_box=BoundingBox(40, 26, 60, 46))
    L_2 = ButtonDef(ButtonHardwareSource.MCP2, 4, bounding_box=BoundingBox(40, 55, 60, 76))
    L_3 = ButtonDef(ButtonHardwareSource.MCP2, 1, bounding_box=BoundingBox(40, 85, 60, 105))
    L_FRONT_F = ButtonDef(ButtonHardwareSource.MCP2, 5, bounding_box=BoundingBox(44, 3, 55, 20))
    L_B_FLAT = ButtonDef(ButtonHardwareSource.MCP2, 9, bounding_box=BoundingBox(59, 47, 68, 55))
    L_D = ButtonDef(ButtonHardwareSource.MCP2, 7, bounding_box=BoundingBox(94, 28, 106, 48))
    L_E_FLAT = ButtonDef(ButtonHardwareSource.MCP2, 13, bounding_box=BoundingBox(79, 14, 91, 34))
    L_F = ButtonDef(ButtonHardwareSource.MCP2, 8, bounding_box=BoundingBox(78, 36, 90, 56))
    L_G_SHARP = ButtonDef(ButtonHardwareSource.MCP2, 2, bounding_box=BoundingBox(69, 94, 96, 102))
    L_LOW_C_SHARP = ButtonDef(ButtonHardwareSource.MCP2, 11, bounding_box=BoundingBox(84, 105, 96, 119))
    L_LOW_B = ButtonDef(ButtonHardwareSource.MCP2, 12, bounding_box=BoundingBox(69, 105, 81, 119))
    L_LOW_B_FLAT = ButtonDef(ButtonHardwareSource.MCP2, 3, bounding_box=BoundingBox(68, 123, 97, 139))

    # Non-note buttons
    L_SELECT = ButtonDef(ButtonHardwareSource.MCP2, 0, is_fingering=False)

    ALL = (R_F_SHARP, R_HIGH_F_SHARP, R_C, R_E, R_1, R_2, R_3, R_B_FLAT, R_LOW_E_FLAT, R_LOW_C, L_1, L_2, L_3, L_FRONT_F, L_B_FLAT, L_D, L_E_FLAT, L_F, L_G_SHARP, L_LOW_C_SHARP, L_LOW_B, L_LOW_B_FLAT, L_OCTAVE, L_SELECT)
