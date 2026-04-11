import asyncio

import adafruit_imageload
import displayio

from data.notes import Notes, Accidental
from hardware.buttons import Buttons
from states.play_state import PlayState


class ScaleDrillState(PlayState):
    def __init__(self, hardware, payload, config):
        self.drill_name = payload.get("name", "Unknown Drill")
        super().__init__(hardware, config, title=self.drill_name)

        note_names = payload.get("notes", [])
        self.notes = [Notes.get_note_by_name(name) for name in note_names if Notes.get_note_by_name(name) is not None]

        # set up drill note display
        drill_note_bitmap, drill_note_palette = adafruit_imageload.load(
            "data/img/half_note_white.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        drill_note_palette.make_transparent(1)
        drill_note_palette[0] = 0x00AA00
        self.drill_note_sprite = displayio.TileGrid(drill_note_bitmap, pixel_shader=drill_note_palette, x=PlayState.STAFF_X_START + 60,
                                              y=PlayState.OFF_SCREEN_Y)
        self.ui_group.append(self.drill_note_sprite)

        # Load Staff Lines
        staff_bitmap, staff_palette = adafruit_imageload.load(
            "data/img/staff_lines_white.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )

        # use staff for ledger lines
        self.drill_c_ledger_line = displayio.TileGrid(staff_bitmap, pixel_shader=drill_note_palette, x=PlayState.STAFF_X_START + 61, y=PlayState.OFF_SCREEN_Y, tile_width=32, tile_height=16)
        self.drill_a_ledger_line = displayio.TileGrid(staff_bitmap, pixel_shader=drill_note_palette, x=PlayState.STAFF_X_START + 61, y=PlayState.OFF_SCREEN_Y, tile_width=32, tile_height=16)
        self.drill_high_c_ledger_line = displayio.TileGrid(staff_bitmap, pixel_shader=drill_note_palette, x=PlayState.STAFF_X_START + 61, y=PlayState.OFF_SCREEN_Y, tile_width=32, tile_height=16)
        self.drill_e_ledger_line = displayio.TileGrid(staff_bitmap, pixel_shader=drill_note_palette, x=PlayState.STAFF_X_START + 61, y=PlayState.OFF_SCREEN_Y, tile_width=32, tile_height=16)

        self.ui_group.append(self.drill_c_ledger_line)
        self.ui_group.append(self.drill_a_ledger_line)
        self.ui_group.append(self.drill_high_c_ledger_line)
        self.ui_group.append(self.drill_e_ledger_line)

        #Load sharp
        sharp_bitmap, sharp_palette = adafruit_imageload.load(
            "data/img/sharp_white.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        self.drill_sharp_sprite = displayio.TileGrid(sharp_bitmap, pixel_shader=drill_note_palette, x=PlayState.STAFF_X_START + 40, y=PlayState.OFF_SCREEN_Y)
        self.ui_group.append(self.drill_sharp_sprite)

        #Load flat
        flat_bitmap, flat_palette = adafruit_imageload.load(
            "data/img/flat_white.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        self.drill_flat_sprite = displayio.TileGrid(flat_bitmap, pixel_shader=drill_note_palette, x=PlayState.STAFF_X_START + 40, y=PlayState.OFF_SCREEN_Y)
        self.ui_group.append(self.drill_flat_sprite)

    async def run(self):
        while self.is_running:
            self.hw.update_button_states()

            if Buttons.L_SELECT.just_pressed:
                # exit if select button pressed
                self.is_running = False
                break

            # show current drill note
            self.draw_drill_note(self.notes[0])

            # show playing note
            target_note = self.hw.get_current_note()
            await self.process_playing_note(target_note)

            # yield control for other code to run
            await asyncio.sleep(0.001)

    def draw_drill_note(self, note):
        self.drill_note_sprite.y = note.staff_y_coord
        self.decorate_note(note, self.drill_note_sprite, self.drill_sharp_sprite, self.drill_flat_sprite, self.drill_c_ledger_line, self.drill_a_ledger_line, self.drill_high_c_ledger_line, self.drill_e_ledger_line)