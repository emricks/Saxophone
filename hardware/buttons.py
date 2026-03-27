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


class Buttons:
    # Buttons from onboard GPIO
    BTN_SELECT = ButtonDef(ButtonHardwareSource.ONBOARD, board.D13)

    # Buttons from MCP GPIO
    RIGHT_INDEX = ButtonDef(ButtonHardwareSource.MCP, 0, fingering_bit=0)
    RIGHT_MIDDLE = ButtonDef(ButtonHardwareSource.MCP, 1, fingering_bit=1)

    ALL = (BTN_SELECT, RIGHT_INDEX, RIGHT_MIDDLE)
