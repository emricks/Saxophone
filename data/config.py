
class Config:
    def __init__(self):
        self.color_data = ColorConfig()


class ColorConfig:
    def __init__(self, name="Default", bg_color=0x0000FF, chart_color=0xFFFFFF, fg_color=0xFFFFFF,
                    fingering_color=0xFF0000):
        self.name = name
        self.bg_color = bg_color
        self.chart_color = chart_color
        self.fg_color = fg_color
        self.fingering_color = fingering_color

