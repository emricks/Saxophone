import asyncio
import bitmaptools
import displayio
import terminalio
import adafruit_imageload
from adafruit_display_text import label
from data.notes import Accidental, Notes
from hardware.buttons import Buttons
from hardware.saxophone import SaxHardware


class PlayState:
    OFF_SCREEN_Y = 240
    C_LEDGER_LINE_Y = 194

    def __init__(self, hardware):
        self.hw = hardware
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
            text="Free Play",
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
        staff_x_start = 32 # Start a bit in from the left
        
        self.staff_1 = displayio.TileGrid(staff_bitmap, pixel_shader=staff_palette, x=staff_x_start, y=staff_y)
        self.staff_2 = displayio.TileGrid(staff_bitmap, pixel_shader=staff_palette, x=staff_x_start + 60, y=staff_y)
        self.staff_3 = displayio.TileGrid(staff_bitmap, pixel_shader=staff_palette, x=staff_x_start + 61, y=PlayState.OFF_SCREEN_Y, tile_width=32, tile_height=16)
        
        self.ui_group.append(self.staff_1)
        self.ui_group.append(self.staff_2)
        self.ui_group.append(self.staff_3)

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

        # Load Half Note
        note_bitmap, note_palette = adafruit_imageload.load(
            "data/img/half_note_white.png",
            bitmap=displayio.Bitmap, 
            palette=displayio.Palette
        )

        # Make color index 1 transparent
        note_palette.make_transparent(1)
        
        # Place note on the staff (starting position will be updated in run)
        self.note_sprite = displayio.TileGrid(note_bitmap, pixel_shader=note_palette, x=staff_x_start + 60, y=PlayState.OFF_SCREEN_Y)
        self.ui_group.append(self.note_sprite)

        #Load sharp
        sharp_bitmap, sharp_palette = adafruit_imageload.load(
            "data/img/sharp_white.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        sharp_palette.make_transparent(1)
        self.sharp_sprite = displayio.TileGrid(sharp_bitmap, pixel_shader=sharp_palette, x=staff_x_start + 40, y=PlayState.OFF_SCREEN_Y)
        self.ui_group.append(self.sharp_sprite)

        flat_bitmap, flat_palette = adafruit_imageload.load(
            "data/img/flat_white.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        flat_palette.make_transparent(1)
        self.flat_sprite = displayio.TileGrid(flat_bitmap, pixel_shader=flat_palette, x=staff_x_start + 40, y=PlayState.OFF_SCREEN_Y)
        self.ui_group.append(self.flat_sprite)

        # load chart
        chart_bitmap, chart_palette = adafruit_imageload.load(
            "data/img/sax_fingering_blank.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        chart_palette.make_transparent(1)
        self.chart_sprite = displayio.TileGrid(chart_bitmap, pixel_shader=chart_palette, x=210, y=0)
        self.ui_group.append(self.chart_sprite)

        self.blit_bitmap, blit_palette = adafruit_imageload.load(
            "data/img/sax_fingering_blit.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        self.unblit_bitmap, unblit_palette = adafruit_imageload.load(
            "data/img/sax_fingering_unblit.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )

    async def hide_notes(self):
        # remove notes visually at/after notes stop playing
        await asyncio.sleep(SaxHardware.NOTE_RELEASE_TIME)
        self.note_sprite.y = PlayState.OFF_SCREEN_Y
        self.sharp_sprite.y = PlayState.OFF_SCREEN_Y
        self.flat_sprite.y = PlayState.OFF_SCREEN_Y
        self.staff_3.y = PlayState.OFF_SCREEN_Y

    def update_chart(self):
        for button in Buttons.ALL:
            if button.just_pressed and button.bounding_box is not None:
                box = button.bounding_box
                bitmaptools.blit(self.chart_sprite.bitmap, self.blit_bitmap, x=box.x0, y=box.y0, x1=0, y1=0,
                                 x2=box.calculate_width(),
                                 y2=box.calculate_height(),
                                 skip_dest_index=1)
            elif button.just_released and button.bounding_box is not None:
                box = button.bounding_box
                bitmaptools.blit(self.chart_sprite.bitmap, self.unblit_bitmap, x=box.x0, y=box.y0, x1=0, y1=0,
                                 x2=box.calculate_width(),
                                 y2=box.calculate_height(),
                                 skip_dest_index=1)



    async def run(self):
        self.current_note_playing = None
        self.hw.stop_note()
        await self.hide_notes()

        while self.is_running:
            self.hw.update_button_states()
            self.update_chart()

            if Buttons.R_B_FLAT.just_pressed:
                self.is_running = False
                break

            # 2. Handle Note Logic
            target_note = self.hw.get_current_note()

            if target_note is None:
                self.hw.stop_note()
                await self.hide_notes()
                self.current_note_playing = None
                continue

            # 3. Apply changes if the note changed
            if target_note != self.current_note_playing:
                self.hw.stop_note()
                await self.hide_notes()

                if target_note is not None:
                    self.hw.play_note(target_note.midi_number)
                    self.note_sprite.y = target_note.staff_y_coord

                    if target_note.accidental is Accidental.SHARP:
                        self.sharp_sprite.y = self.note_sprite.y + 36
                    if target_note.accidental is Accidental.FLAT:
                        self.flat_sprite.y = self.note_sprite.y + 24
                    if target_note is Notes.C_4:
                        self.staff_3.y = PlayState.C_LEDGER_LINE_Y

                self.current_note_playing = target_note

            self.hw.display.refresh()
            await asyncio.sleep(0.001)

        # STOP AUDIO: Release notes before exiting the loop
        self.hw.stop_note()
        await self.hide_notes()
