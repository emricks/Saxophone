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
    # Buttons from onboard GPIO
    BTN_SELECT = ButtonDef(ButtonHardwareSource.ONBOARD, board.D13)
    BTN_UP = ButtonDef(ButtonHardwareSource.ONBOARD, board.D12)
    BTN_DOWN = ButtonDef(ButtonHardwareSource.ONBOARD, board.D11)

    # Buttons from MCP GPIO
    RIGHT_INDEX = ButtonDef(ButtonHardwareSource.MCP, 0, fingering_bit=0)
    RIGHT_MIDDLE = ButtonDef(ButtonHardwareSource.MCP, 1, fingering_bit=1)
    RIGHT_RING= ButtonDef(ButtonHardwareSource.MCP, 2, fingering_bit=2)
    RIGHT_PINKY = ButtonDef(ButtonHardwareSource.MCP, 3, fingering_bit=3)

    ALL = (BTN_SELECT, BTN_UP, BTN_DOWN, RIGHT_INDEX, RIGHT_MIDDLE, RIGHT_RING, RIGHT_PINKY)
