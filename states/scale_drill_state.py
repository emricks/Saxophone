import asyncio
import random
import time

import adafruit_imageload
import displayio

from data.notes import Notes
from hardware.buttons import Buttons
from states.play_state import PlayState


class ScaleDrillState(PlayState):
    def __init__(self, hardware, payload, config):
        self.drill_name = payload.get("name", "Unknown Drill")
        super().__init__(hardware, config, title=self.drill_name)

        # Scoring attributes
        self.total_score = 0
        self.note_start_time = None
        self.note_played_time = None
        self.MAX_POSSIBLE_PER_NOTE = 5.0  # Placeholder constant

        note_names = payload.get("notes", [])
        self.notes = [Notes.get_note_by_name(name) for name in note_names if Notes.get_note_by_name(name) is not None]
        self.random_notes = []
        for i in range(len(self.notes)):
            self.random_notes.append(random.choice(self.notes))

        self.notes += self.random_notes

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
        drill_note_index = 0
        self.note_start_time = time.monotonic()

        while self.is_running:
            if self.hw.display.root_group != self.ui_group:
                self.hw.display.root_group = self.ui_group

            self.hw.update_button_states()

            if Buttons.L_SELECT.just_pressed or drill_note_index == len(self.notes):
                # exit if select button pressed
                self.is_running = False
                break

            # show current drill note
            self.draw_drill_note(self.notes[drill_note_index])

            # show playing note
            target_note = self.hw.get_current_note()
            await self.process_playing_note(target_note)

            breathing = self.hw.breath_sensor.breath_sensor_triggered
            current_time = time.monotonic()

            # 1. DETECTION: Did they start playing the right note?
            if target_note == self.notes[drill_note_index] and breathing:
                if self.note_played_time is None:
                    self.note_played_time = current_time
                    # print(f"Note started! Waiting for 1s hold...")
            else:
                # If they stop breathing or play the wrong note, the "hold" is broken
                if self.note_played_time is not None:
                    self.note_played_time = None
                    # print("Hold broken! Must start hold from beginning.")

            # 2. VALIDATION: Have they held it long enough to earn the score?
            if self.note_played_time is not None:
                if current_time - self.note_played_time >= 1.0:
                    # SUCCESS! Now we calculate and award the score
                    if self.note_start_time is None:
                        self.note_start_time = self.note_played_time

                    reaction_time = self.note_played_time - self.note_start_time
                    score = max(0, self.MAX_POSSIBLE_PER_NOTE - reaction_time)
                    self.total_score += score

                    print(f"Success! Score awarded: {score:.2f}")

                    # Move to next note and reset state
                    drill_note_index += 1
                    self.note_start_time = time.monotonic()
                    self.note_played_time = None
                    print(f"Moving to next note. Total score so far: {self.total_score:.2f}")

            # yield control for other code to run
            await asyncio.sleep(0.001)

        self.hw.stop_note()
        print(f"Drill finished! Final total score: {self.total_score:.2f}")

    def draw_drill_note(self, note):
        self.drill_note_sprite.y = note.staff_y_coord
        self.decorate_note(note, self.drill_note_sprite, self.drill_sharp_sprite, self.drill_flat_sprite, self.drill_c_ledger_line, self.drill_a_ledger_line, self.drill_high_c_ledger_line, self.drill_e_ledger_line)
