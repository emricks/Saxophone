import asyncio
import displayio
import terminalio
from adafruit_display_text import label

from hardware.buttons import Buttons


class DrillState:
    def __init__(self, hardware, payload):
        self.hw = hardware
        self.drill_name = payload.get("name", "Unknown Drill")
        self.notes = payload.get("notes", [])
        self.is_running = True
        self.current_note_playing = None

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
        self.current_note_playing = None
        self.hw.stop_note()

        while self.is_running:
            self.hw.update_button_states()

            if Buttons.BTN_SELECT.is_pressed:
                self.is_running = False
                break

            # 2. Handle Note Logic
            target_note = self.hw.get_current_note()

            if target_note is None:
                self.hw.stop_note()
                self.current_note_playing = None
                continue

            # 3. Apply changes if the note changed
            if target_note != self.current_note_playing:
                self.hw.stop_note()

                if target_note is not None:
                    self.hw.play_note(target_note.midi_number)

                self.current_note_playing = target_note

            self.hw.display.refresh()
            await asyncio.sleep(0.01)

        # STOP AUDIO: Release notes before exiting the loop
        self.hw.stop_note()
