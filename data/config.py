import json

CONFIG_PATH = "config.json"


def _to_dict(obj):
    result = {}
    for key, val in vars(obj).items():
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

    @classmethod
    def load_config(cls) -> "Config":
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
            config = cls()
            _apply_dict(config, data)
            return config
        except (OSError, ValueError):
            config = cls()
            config.persist()
            return config

    def persist(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(_to_dict(self), f)


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

