
import board


class ButtonHardwareSource:
    ONBOARD = "ONBOARD"
    MCP = "MCP"


class ButtonDef:
    def __init__(self, hw_source, hw_pin, fingering_bit=None):
        self.hw_source = hw_source  # e.g., 'ONBOARD' or 'MCP'
        self.hw_pin = hw_pin  # board.D11 or MCP pin integer (0, 1, etc.)
        self.fingering_bit = fingering_bit  # button position in a fingering mask
        self.is_pressed = False
        self.was_pressed = False

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
    R_F_SHARP = ButtonDef(ButtonHardwareSource.ONBOARD, board.D13, fingering_bit=4)
    R_HIGH_F_SHARP = ButtonDef(ButtonHardwareSource.MCP, 0, fingering_bit=3)
    R_C = ButtonDef(ButtonHardwareSource.ONBOARD, board.D11, fingering_bit=6)
    R_E = ButtonDef(ButtonHardwareSource.MCP, 1, fingering_bit=5)
    R_1 = ButtonDef(ButtonHardwareSource.MCP, 2, fingering_bit=0)
    R_2 = ButtonDef(ButtonHardwareSource.ONBOARD, board.D12, fingering_bit=1)
    R_3 = ButtonDef(ButtonHardwareSource.MCP, 3, fingering_bit=2)
    R_B_FLAT = ButtonDef(ButtonHardwareSource.MCP, 4, fingering_bit=7)
    R_LOW_E_FLAT = ButtonDef(ButtonHardwareSource.MCP, 5, fingering_bit=8)
    R_LOW_C = ButtonDef(ButtonHardwareSource.MCP, 6, fingering_bit=9)

    # TODO: Left hand
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

    ALL = (R_F_SHARP, R_HIGH_F_SHARP, R_C, R_E, R_1, R_2, R_3, R_B_FLAT, R_LOW_E_FLAT, R_LOW_C)
