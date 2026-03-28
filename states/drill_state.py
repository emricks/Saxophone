import asyncio
import displayio
import terminalio
import adafruit_imageload
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

        # Drill Name along the top
        self.title_label = label.Label(
            terminalio.FONT,
            text=f"{self.drill_name}",
            color=0xFFFFFF,
            scale=2,
            x=10,
            y=15
        )
        self.ui_group.append(self.title_label)
        
        # Load Staff Lines (69x69)
        staff_bitmap, staff_palette = adafruit_imageload.load(
            "data/img/staff_lines_white.png", 
            bitmap=displayio.Bitmap, 
            palette=displayio.Palette
        )
        # Make color index 1 transparent
        staff_palette.make_transparent(1) 
        
        # Two copies of the staff side-by-side, centered vertically
        staff_y = (240 // 2) - (69 // 2) # Center vertically
        staff_x_start = 60 # Start a bit in from the left
        
        self.staff_1 = displayio.TileGrid(staff_bitmap, pixel_shader=staff_palette, x=staff_x_start, y=staff_y)
        self.staff_2 = displayio.TileGrid(staff_bitmap, pixel_shader=staff_palette, x=staff_x_start + 69, y=staff_y)
        
        self.ui_group.append(self.staff_1)
        self.ui_group.append(self.staff_2)

        # Load Treble Clef (36x72)
        clef_bitmap, clef_palette = adafruit_imageload.load(
            "data/img/treble_clef_white.png",
            bitmap=displayio.Bitmap, 
            palette=displayio.Palette
        )
        # Make color index 1 transparent
        clef_palette.make_transparent(1)
        
        # Place treble clef on the far left of the staff
        clef_y = staff_y - 2 # Minor adjustment to align with staff visually
        self.treble_clef = displayio.TileGrid(clef_bitmap, pixel_shader=clef_palette, x=staff_x_start - 20, y=clef_y)
        self.ui_group.append(self.treble_clef)

        # Load Half Note (36x72)
        note_bitmap, note_palette = adafruit_imageload.load(
            "data/img/half_note_white.png", 
            bitmap=displayio.Bitmap, 
            palette=displayio.Palette
        )
        # Make color index 1 transparent
        note_palette.make_transparent(1)
        
        # Place note on the staff (starting position will be updated in run)
        self.note_sprite = displayio.TileGrid(note_bitmap, pixel_shader=note_palette, x=staff_x_start + 40, y=staff_y)
        self.ui_group.append(self.note_sprite)

    async def run(self):
        self.current_note_playing = None
        self.hw.stop_note()

        while self.is_running:
            self.hw.update_button_states()

            if Buttons.BTN_SELECT.just_pressed:
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
                    
                    # Update note sprite position based on staff_y_coord
                    if hasattr(target_note, 'staff_y_coord'):
                        self.note_sprite.y = target_note.staff_y_coord

                self.current_note_playing = target_note

            self.hw.display.refresh()
            await asyncio.sleep(0.01)

        # STOP AUDIO: Release notes before exiting the loop
        self.hw.stop_note()
