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


def _pretty_dump(obj, f, level: int = 0) -> None:
    if isinstance(obj, dict):
        if not obj:
            f.write("{}")
            return
        indent = "  " * level
        inner = "  " * (level + 1)
        f.write("{\n")
        items = list(obj.items())
        for i, (key, val) in enumerate(items):
            f.write(inner)
            f.write(json.dumps(key))
            f.write(": ")
            _pretty_dump(val, f, level + 1)
            if i < len(items) - 1:
                f.write(",")
            f.write("\n")
        f.write(indent)
        f.write("}")
    else:
        f.write(json.dumps(obj))


class Config:
    def __init__(self):
        self.color_data = ColorConfig()
        self.volume_data = VolumeConfig()
        self.drill_data = DrillConfig()
        self.button_data = ButtonConfig()

    @classmethod
    def load_config(cls) -> "Config":
        config = cls()
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
            _apply_dict(config, data)
            print("Loaded config from", CONFIG_PATH, ":", data)
        except (OSError, ValueError) as e:
            print(f"Could not load {CONFIG_PATH} ({e}); writing defaults")
            config.persist()
        Buttons.apply_config(config.button_data)
        return config

    def persist(self) -> None:
        try:
            with open(CONFIG_PATH, "w") as f:
                _pretty_dump(_to_dict(self), f)
        except OSError as e:
            # Filesystem is host-writable (dev mode from boot.py).
            # Hold 3+ buttons on MCP1 at boot to enter run mode for device writes.
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
    # Allowed levels: 1% floor, then 10% steps up to 100%.
    LEVELS = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]

    def __init__(self, volume=0.3):
        self.volume = volume

    def step_up(self):
        for level in self.LEVELS:
            if level > self.volume + 0.001:
                self.volume = level
                return

    def step_down(self):
        for level in reversed(self.LEVELS):
            if level < self.volume - 0.001:
                self.volume = level
                return

    def percent(self):
        return int(round(self.volume * 100))


class DrillConfig:
    """Persisted defaults for drill timing. Used by ScaleDrillState at startup;
    the live session value (ScaleDrillState.SESSION_MODE) is seeded from
    `default_mode` on boot and may diverge mid-session via the ready-screen
    toggle. The Drill settings screen writes both back at the same time.

    Owns the canonical MODE_TIMED / MODE_EASY constants — ScaleDrillState
    re-exports them so callers don't need to import data.config to compare
    against a mode value."""

    MODE_TIMED = "timed"
    MODE_EASY = "easy"
    MODES = (MODE_TIMED, MODE_EASY)

    BPM_STEP = 2
    BPM_MIN = 40
    BPM_MAX = 160

    def __init__(self, default_bpm=56, default_mode=MODE_TIMED, hold_factor=0.75):
        self.default_bpm = default_bpm
        self.default_mode = default_mode
        # Fraction of musical duration that counts as fully satisfied — the
        # remaining (1 - hold_factor) is breathing room. Used for both fill
        # display (reaches 100% at this point) and timed-mode scoring.
        self.hold_factor = hold_factor

    def step_bpm_up(self):
        self.default_bpm = min(self.default_bpm + self.BPM_STEP, self.BPM_MAX)

    def step_bpm_down(self):
        self.default_bpm = max(self.default_bpm - self.BPM_STEP, self.BPM_MIN)

    def toggle_mode(self):
        self.default_mode = (
            DrillConfig.MODE_EASY if self.default_mode == DrillConfig.MODE_TIMED
            else DrillConfig.MODE_TIMED
        )


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

