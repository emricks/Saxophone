import asyncio
import bitmaptools
import displayio
import terminalio
import adafruit_imageload
from adafruit_display_text import label

from data.config import ColorConfig
from data.notes import Accidental, Notes
from hardware.buttons import Buttons
from hardware.saxophone import SaxHardware


class PlayState:
    OFF_SCREEN_Y = 240
    C_LEDGER_LINE_Y = 208
    A_LEDGER_LINE_Y = 76
    HIGH_C_LEDGER_LINE_Y = 54
    E_LEDGER_LINE_Y = 32

    def __init__(self, hardware, color_data: ColorConfig):
        self.hw = hardware
        self.is_running = True
        self.current_note_playing = None

        self.ui_group = displayio.Group()
        self.hw.display.root_group = self.ui_group

        # Background
        color_bitmap = displayio.Bitmap(320, 240, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = color_data.bg_color
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self.ui_group.append(bg_sprite)

        # Drill Name along the top
        self.title_label = label.Label(
            terminalio.FONT,
            text="Free Play",
            color=color_data.fg_color,
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
        staff_palette[0] = color_data.fg_color
        
        # Two copies of the staff side-by-side, centered vertically
        staff_y = (240 // 2) - (69 // 2) + 11 # Center vertically, move down to allow more room for notes
        staff_x_start = 32 # Start a bit in from the left
        
        self.staff_1 = displayio.TileGrid(staff_bitmap, pixel_shader=staff_palette, x=staff_x_start, y=staff_y)
        self.staff_2 = displayio.TileGrid(staff_bitmap, pixel_shader=staff_palette, x=staff_x_start + 60, y=staff_y)
        self.c_ledger_line = displayio.TileGrid(staff_bitmap, pixel_shader=staff_palette, x=staff_x_start + 61, y=PlayState.OFF_SCREEN_Y, tile_width=32, tile_height=16)
        self.a_ledger_line = displayio.TileGrid(staff_bitmap, pixel_shader=staff_palette, x=staff_x_start + 61, y=PlayState.OFF_SCREEN_Y, tile_width=32, tile_height=16)
        self.high_c_ledger_line = displayio.TileGrid(staff_bitmap, pixel_shader=staff_palette, x=staff_x_start + 61, y=PlayState.OFF_SCREEN_Y, tile_width=32, tile_height=16)
        self.e_ledger_line = displayio.TileGrid(staff_bitmap, pixel_shader=staff_palette, x=staff_x_start + 61, y=PlayState.OFF_SCREEN_Y, tile_width=32, tile_height=16)

        self.ui_group.append(self.staff_1)
        self.ui_group.append(self.staff_2)
        self.ui_group.append(self.c_ledger_line)
        self.ui_group.append(self.a_ledger_line)
        self.ui_group.append(self.high_c_ledger_line)
        self.ui_group.append(self.e_ledger_line)

        # Load Treble Clef (36x72)
        clef_bitmap, clef_palette = adafruit_imageload.load(
            "data/img/treble_clef_white.png",
            bitmap=displayio.Bitmap, 
            palette=displayio.Palette
        )
        # Make color index 1 transparent
        clef_palette.make_transparent(1)
        clef_palette[0] = color_data.fg_color
        
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
        note_palette[0] = color_data.fg_color
        
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
        sharp_palette[0] = color_data.fg_color
        self.sharp_sprite = displayio.TileGrid(sharp_bitmap, pixel_shader=sharp_palette, x=staff_x_start + 40, y=PlayState.OFF_SCREEN_Y)
        self.ui_group.append(self.sharp_sprite)

        flat_bitmap, flat_palette = adafruit_imageload.load(
            "data/img/flat_white.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        flat_palette.make_transparent(1)
        flat_palette[0] = color_data.fg_color
        self.flat_sprite = displayio.TileGrid(flat_bitmap, pixel_shader=flat_palette, x=staff_x_start + 40, y=PlayState.OFF_SCREEN_Y)
        self.ui_group.append(self.flat_sprite)

        # load chart
        chart_bitmap, chart_palette = adafruit_imageload.load(
            "data/img/sax_fingering_blank.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        chart_palette.make_transparent(1)
        chart_palette[0] = color_data.chart_color
        chart_palette[2] = color_data.fingering_color
        self.chart_sprite = displayio.TileGrid(chart_bitmap, pixel_shader=chart_palette, x=210, y=0)

        self.blit_bitmap, blit_palette = adafruit_imageload.load(
            "data/img/sax_fingering_blit.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        blit_palette[2] = color_data.fingering_color
        self.unblit_bitmap, unblit_palette = adafruit_imageload.load(
            "data/img/sax_fingering_unblit.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        unblit_palette[0] = color_data.chart_color

    async def hide_notes(self):
        # remove notes visually at/after notes stop playing
        await asyncio.sleep(SaxHardware.NOTE_RELEASE_TIME)
        self.note_sprite.y = PlayState.OFF_SCREEN_Y
        self.sharp_sprite.y = PlayState.OFF_SCREEN_Y
        self.flat_sprite.y = PlayState.OFF_SCREEN_Y
        self.c_ledger_line.y = PlayState.OFF_SCREEN_Y
        self.a_ledger_line.y = PlayState.OFF_SCREEN_Y
        self.high_c_ledger_line.y = PlayState.OFF_SCREEN_Y
        self.e_ledger_line.y = PlayState.OFF_SCREEN_Y

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
        self.ui_group.append(self.chart_sprite)
        self.current_note_playing = None
        self.hw.stop_note()
        await self.hide_notes()

        while self.is_running:
            self.hw.update_button_states()
            self.update_chart()

            if Buttons.L_SELECT.just_pressed:
                self.is_running = False
                break

            # 2. Handle Note Logic
            target_note = self.hw.get_current_note()
            breathing = self.hw.breath_sensor.breath_sensor_triggered

            if target_note is None or not breathing:
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
                    if target_note in Notes.C_LINE:
                        self.c_ledger_line.y = PlayState.C_LEDGER_LINE_Y
                    if target_note in Notes.A_LINE:
                        self.a_ledger_line.y = PlayState.A_LEDGER_LINE_Y
                    if target_note in Notes.HIGH_C_LINE:
                        self.high_c_ledger_line.y = PlayState.HIGH_C_LEDGER_LINE_Y
                    if target_note in Notes.E_LINE:
                        self.e_ledger_line.y = PlayState.E_LEDGER_LINE_Y

                self.current_note_playing = target_note

            self.hw.display.refresh()
            await asyncio.sleep(0.001)

        # STOP AUDIO: Release notes before exiting the loop
        self.hw.stop_note()
