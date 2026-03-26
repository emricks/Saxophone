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
        # Fingering Dictionary: Maps button combos to MIDI notes
        # UP (Bit 0) = 1
        # SELECT (Bit 1) = 2
        # DOWN (Bit 2) = 4
        FINGERINGS = {
            0: None,  # Nothing pressed = Silence
            1: 54,  # UP only
            4: 56,  # DOWN only
            5: 58,  # UP + DOWN together (1 + 4 = 5)
            # Add more combos here!
        }

        # Ensure we start in a known silent state
        self.current_note_playing = None
        self.hw.stop_note()

        while self.is_running:
            # 1. Drain the event queue to keep our hardware tracking array 100% up to date
            while self.hw.get_button_event():
                pass

                # 2. Build the bitmask based on the CURRENT physical state of the buttons
            mask = 0
            if self.hw.key_states[self.hw.BTN_UP]:     mask |= 1
            if self.hw.key_states[self.hw.BTN_SELECT]: mask |= 2
            if self.hw.key_states[self.hw.BTN_DOWN]:   mask |= 4

            # (Optional) Secret exit combo: Press SELECT (2) by itself to quit
            if mask == 2:
                self.is_running = False
                break

            # 3. Look up the corresponding note for this specific fingering
            target_note = FINGERINGS.get(mask, None)

            # 4. If the fingering changed, update the audio!
            if target_note != self.current_note_playing:
                self.hw.stop_note()  # Always cut the old note off first

                if target_note is not None:
                    self.hw.play_note(target_note)

                self.current_note_playing = target_note

            self.hw.display.refresh()
            await asyncio.sleep(0.01)

        # STOP AUDIO: Release notes before exiting the loop
        self.hw.stop_note()