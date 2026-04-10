import asyncio
import displayio
import terminalio
import adafruit_imageload
from adafruit_display_text import label

from hardware.buttons import Buttons
from states.play_state import PlayState


class ScaleDrillState(PlayState):
    def __init__(self, hardware, payload, color_data):
        super().__init__(hardware, color_data)
        self.drill_name = payload.get("name", "Unknown Drill")
        self.notes = payload.get("notes", [])
