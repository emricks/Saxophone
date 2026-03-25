import asyncio
import displayio
import terminalio
from adafruit_display_text import label


class DrillState:
    def __init__(self, hardware, payload):
        self.hw = hardware
        self.drill_name = payload.get("name", "Unknown Drill")
        self.notes = payload.get("notes", [])
        self.is_running = True

        self.ui_group = displayio.Group()
        self.hw.display.root_group = self.ui_group

        # Blue Background
        color_bitmap = displayio.Bitmap(320, 240, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0x0000AA
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self.ui_group.append(bg_sprite)

        # Moving text
        self.text_y = 100
        self.title_label = label.Label(
            terminalio.FONT,
            text=f"{self.drill_name}\nComing Soon!",
            color=0xFFFFFF,
            scale=2,
            x=60,
            y=self.text_y
        )
        self.notes_label = label.Label(
            terminalio.FONT,
            text=f"{self.notes}",
            color=0xFFFFFF,
            scale=1,
            x=60,
            y=self.text_y + 80
        )
        self.ui_group.append(self.title_label)
        self.ui_group.append(self.notes_label)

    async def run(self):
        # START AUDIO: Press Concert Gb3 (Alto Sax written Eb4)
        alto_eb_midi_note = 54
        self.hw.play_note(alto_eb_midi_note)

        while self.is_running:
            event = self.hw.get_button_event()

            if event and event.pressed:
                if event.key_number == self.hw.BTN_UP:
                    self.text_y -= 10
                    self.title_label.y = self.text_y

                elif event.key_number == self.hw.BTN_DOWN:
                    self.text_y += 10
                    self.title_label.y = self.text_y

                elif event.key_number == self.hw.BTN_SELECT:
                    self.is_running = False

            await asyncio.sleep(0.01)

        # STOP AUDIO: Release all notes right before exiting the loop
        self.hw.stop_note()