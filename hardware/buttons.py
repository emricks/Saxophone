
import board


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
    def __init__(self, hw_source, hw_pin, fingering_bit=None, bounding_box: BoundingBox = None):
        self.hw_source = hw_source  # e.g., 'ONBOARD' or 'MCP1'
        self.hw_pin = hw_pin  # board.D11 or MCP pin integer (0, 1, etc.)
        self.fingering_bit = fingering_bit  # button position in a fingering mask
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
    R_F_SHARP = ButtonDef(ButtonHardwareSource.MCP1, 4, fingering_bit=4, bounding_box=BoundingBox(15, 176, 36, 186))
    R_HIGH_F_SHARP = ButtonDef(ButtonHardwareSource.MCP1, 0, fingering_bit=3, bounding_box=BoundingBox(21, 145, 33, 170))
    R_C = ButtonDef(ButtonHardwareSource.MCP1, 7, fingering_bit=6, bounding_box=BoundingBox(7, 124, 18, 136))
    R_E = ButtonDef(ButtonHardwareSource.MCP1, 9, fingering_bit=5, bounding_box=BoundingBox(7, 106, 18, 119))
    R_1 = ButtonDef(ButtonHardwareSource.MCP1, 6, fingering_bit=0, bounding_box=BoundingBox(40, 129, 60, 149))
    R_2 = ButtonDef(ButtonHardwareSource.MCP1, 8, fingering_bit=1, bounding_box=BoundingBox(40, 158, 60, 178))
    R_3 = ButtonDef(ButtonHardwareSource.MCP1, 1, fingering_bit=2, bounding_box=BoundingBox(40, 188, 60, 207))
    R_B_FLAT = ButtonDef(ButtonHardwareSource.MCP1, 5, fingering_bit=7, bounding_box=BoundingBox(7, 141, 18, 158))
    R_LOW_E_FLAT = ButtonDef(ButtonHardwareSource.MCP1, 3, fingering_bit=8, bounding_box=BoundingBox(2, 199, 30, 215))
    R_LOW_C = ButtonDef(ButtonHardwareSource.MCP1, 2, fingering_bit=9, bounding_box=BoundingBox(2, 220, 32, 238))

    # TODO: Left hand
    L_OCTAVE = ButtonDef(ButtonHardwareSource.MCP2, 6, fingering_bit=23)
    L_1 = ButtonDef(ButtonHardwareSource.MCP2, 10, fingering_bit=10)
    L_2 = ButtonDef(ButtonHardwareSource.MCP2, 4, fingering_bit=11)
    L_3 = ButtonDef(ButtonHardwareSource.MCP2, 1, fingering_bit=12)
    L_FRONT_F = ButtonDef(ButtonHardwareSource.MCP2, 5, fingering_bit=13)
    L_B_FLAT = ButtonDef(ButtonHardwareSource.MCP2, 9, fingering_bit=14)
    L_D = ButtonDef(ButtonHardwareSource.MCP2, 7, fingering_bit=15)
    L_E_FLAT = ButtonDef(ButtonHardwareSource.MCP2, 13, fingering_bit=16)
    L_F = ButtonDef(ButtonHardwareSource.MCP2, 8, fingering_bit=17)
    L_G_SHARP = ButtonDef(ButtonHardwareSource.MCP2, 2, fingering_bit=18)
    L_LOW_C_SHARP = ButtonDef(ButtonHardwareSource.MCP2, 11, fingering_bit=19)
    L_LOW_B = ButtonDef(ButtonHardwareSource.MCP2, 12, fingering_bit=20)
    L_LOW_B_FLAT = ButtonDef(ButtonHardwareSource.MCP2, 3, fingering_bit=21)
    L_SELECT = ButtonDef(ButtonHardwareSource.MCP2, 0, fingering_bit=22)
    # L_OCTAVE
    # L_1
    # L_2
    # L_3
    # L_FRONT_F
    # L_B_FLAT
    # L_D
    # L_E_FLAT
    # L_F
    # L_G_SHARP
    # L_LOW_C_SHARP
    # L_LOW_B
    # L_LOW_B_FLAT

    # TODO: Add select button and possibly "play" button

    ALL = (R_F_SHARP, R_HIGH_F_SHARP, R_C, R_E, R_1, R_2, R_3, R_B_FLAT, R_LOW_E_FLAT, R_LOW_C, L_1, L_2, L_3, L_FRONT_F, L_B_FLAT, L_D, L_E_FLAT, L_F, L_G_SHARP, L_LOW_C_SHARP, L_LOW_B, L_LOW_B_FLAT, L_OCTAVE, L_SELECT)
