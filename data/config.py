import json

from hardware.buttons import ButtonHardwareSource, Buttons

CONFIG_PATH = "config.json"


def _to_dict(obj):
    result = {}
    for key, val in obj.__dict__.items():
        result[key] = _to_dict(val) if hasattr(val, "__dict__") else val
    return result


def _apply_dict(obj, data):
    for key, val in data.items():
        if not hasattr(obj, key):
            continue
        attr = getattr(obj, key)
        if hasattr(attr, "__dict__") and isinstance(val, dict):
            _apply_dict(attr, val)
        else:
            setattr(obj, key, val)


class Config:
    def __init__(self):
        self.color_data = ColorConfig()
        self.volume_data = VolumeConfig()
        self.button_data = ButtonConfig()

    @classmethod
    def load_config(cls) -> "Config":
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
            config = cls()
            _apply_dict(config, data)
        except (OSError, ValueError):
            config = cls()
            config.persist()
        Buttons.apply_config(config.button_data)
        return config

    def persist(self) -> None:
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(_to_dict(self), f)
        except OSError as e:
            # Filesystem is read-only for the device while USB host has it mounted.
            # Run unplugged once to let the device write the bootstrap config.
            print(f"Warning: could not persist config ({e}); using in-memory values.")


class ColorConfig:
    def __init__(self, name="Default", bg_color=0x0000FF, chart_color=0xFFFFFF, fg_color=0xFFFFFF,
                    fingering_color=0xFF0000, drill_note_color=0x00FF00):
        self.name = name
        self.bg_color = bg_color
        self.chart_color = chart_color
        self.fg_color = fg_color
        self.fingering_color = fingering_color
        self.drill_note_color = drill_note_color

class VolumeConfig:
    def __init__(self, volume=0.3):
        self.volume = volume


class ButtonPin:
    def __init__(self, hw_source: str = ButtonHardwareSource.ONBOARD, hw_pin: int = 0):
        self.hw_source = hw_source
        self.hw_pin = hw_pin


class ButtonConfig:
    def __init__(self):
        # Right hand
        self.R_F_SHARP = ButtonPin(ButtonHardwareSource.MCP1, 4)
        self.R_HIGH_F_SHARP = ButtonPin(ButtonHardwareSource.MCP1, 0)
        self.R_C = ButtonPin(ButtonHardwareSource.MCP1, 7)
        self.R_E = ButtonPin(ButtonHardwareSource.MCP1, 9)
        self.R_1 = ButtonPin(ButtonHardwareSource.MCP1, 6)
        self.R_2 = ButtonPin(ButtonHardwareSource.MCP1, 8)
        self.R_3 = ButtonPin(ButtonHardwareSource.MCP1, 1)
        self.R_B_FLAT = ButtonPin(ButtonHardwareSource.MCP1, 5)
        self.R_LOW_E_FLAT = ButtonPin(ButtonHardwareSource.MCP1, 3)
        self.R_LOW_C = ButtonPin(ButtonHardwareSource.MCP1, 2)

        # Left hand
        self.L_OCTAVE = ButtonPin(ButtonHardwareSource.MCP2, 6)
        self.L_1 = ButtonPin(ButtonHardwareSource.MCP2, 10)
        self.L_2 = ButtonPin(ButtonHardwareSource.MCP2, 4)
        self.L_3 = ButtonPin(ButtonHardwareSource.MCP2, 1)
        self.L_FRONT_F = ButtonPin(ButtonHardwareSource.MCP2, 5)
        self.L_B_FLAT = ButtonPin(ButtonHardwareSource.MCP2, 9)
        self.L_D = ButtonPin(ButtonHardwareSource.MCP2, 7)
        self.L_E_FLAT = ButtonPin(ButtonHardwareSource.MCP2, 13)
        self.L_F = ButtonPin(ButtonHardwareSource.MCP2, 8)
        self.L_G_SHARP = ButtonPin(ButtonHardwareSource.MCP2, 2)
        self.L_LOW_C_SHARP = ButtonPin(ButtonHardwareSource.MCP2, 11)
        self.L_LOW_B = ButtonPin(ButtonHardwareSource.MCP2, 12)
        self.L_LOW_B_FLAT = ButtonPin(ButtonHardwareSource.MCP2, 3)

        # Non-note buttons
        self.L_SELECT = ButtonPin(ButtonHardwareSource.MCP2, 0)

