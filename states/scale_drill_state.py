import asyncio
import random
import time

import adafruit_imageload
import displayio
import terminalio
from adafruit_display_text import label

from data.notes import Notes
from hardware.buttons import Buttons
from states.play_state import PlayState


class ScaleDrillState(PlayState):
    def __init__(self, hardware, payload, config):
        self.drill_name = payload.get("name", "Unknown Drill")
        super().__init__(hardware, config, title=self.drill_name)

        self.config = config

        # Scoring attributes
        self.total_score = 0
        self.note_start_time = None
        self.note_played_time = None
        self.MAX_POSSIBLE_PER_NOTE = 5.0  # Placeholder constant
        self.hint_task = None
        self.current_hint_fingering = None

        # Add Score Label
        self.score_label = label.Label(
            terminalio.FONT,
            text="0",
            color=config.color_data.fg_color,
            scale=2,
        )
        self.score_label.anchor_point = (0.5, 0.0)
        self.score_label.anchored_position = (160, 5)
        self.ui_group.append(self.score_label)

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
        
        if self.chart_sprite not in self.ui_group:
            self.ui_group.append(self.chart_sprite)

        while self.is_running:
            if self.hw.display.root_group != self.ui_group:
                self.hw.display.root_group = self.ui_group

            self.hw.update_button_states()

            if Buttons.L_SELECT.just_pressed or drill_note_index == len(self.notes):
                # exit if select button pressed or finished
                break

            current_note = self.notes[drill_note_index]
            # show current drill note
            self.draw_drill_note(current_note)

            # show playing note
            target_note = self.hw.get_current_note()
            await self.process_playing_note(target_note)

            breathing = self.hw.breath_sensor.breath_sensor_triggered
            current_time = time.monotonic()

            # 1. DETECTION: Did they start playing the right note?
            if target_note == current_note and breathing:
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
                if current_time - self.note_played_time >= 0.75:
                    # SUCCESS! Now we calculate and award the score
                    if self.note_start_time is None:
                        self.note_start_time = self.note_played_time

                    reaction_time = self.note_played_time - self.note_start_time
                    score = int(max(0, self.MAX_POSSIBLE_PER_NOTE - reaction_time) * 100)
                    self.total_score += score
                    self.score_label.text = str(self.total_score)

                    # Spawn the animation task
                    asyncio.create_task(self.animate_score_text())

                    print(f"Success! Score awarded: {score}")

                    # Cancel hint cycle if it's running
                    if self.hint_task is not None:
                        self.hint_task.cancel()
                        self.hint_task = None
                    
                    if self.current_hint_fingering is not None:
                        await self.clear_specific_fingering(self.current_hint_fingering)
                        self.current_hint_fingering = None

                    # Move to next note and reset state
                    drill_note_index += 1
                    self.note_start_time = time.monotonic()
                    self.note_played_time = None
                    print(f"Moving to next note. Total score so far: {self.total_score}")
            
            # 3. HINT: If they are taking too long, start cycling the fingerings
            if self.hint_task is None and self.note_start_time is not None:
                if time.monotonic() - self.note_start_time > self.MAX_POSSIBLE_PER_NOTE:
                    self.hint_task = asyncio.create_task(self.cycle_fingerings(current_note))

            # yield control for other code to run
            await asyncio.sleep(0.001)

        # Cancel any leftover hint tasks upon exiting
        if self.hint_task is not None:
            self.hint_task.cancel()
            
        if self.current_hint_fingering is not None:
            await self.clear_specific_fingering(self.current_hint_fingering)
            self.current_hint_fingering = None

        self.hw.stop_note()

        if drill_note_index == len(self.notes):
            await self.show_scoreboard()

    async def cycle_fingerings(self, note):
        fingerings = list(note.button_fingerings)
        try:
            # if only 1 fingering, just show it permanently
            if len(fingerings) == 1:
                self.current_hint_fingering = fingerings[0]
                await self.blit_specific_fingering(self.current_hint_fingering)
                while True:
                    await asyncio.sleep(1.0)
            else:
                while True:
                    for fingering in fingerings:
                        if self.current_hint_fingering is not None:
                            await self.clear_specific_fingering(self.current_hint_fingering)
                        
                        self.current_hint_fingering = fingering
                        await self.blit_specific_fingering(self.current_hint_fingering)
                        await asyncio.sleep(2.0)
        except asyncio.CancelledError:
            pass # Task was intentionally canceled because the user got the note right

    def get_score_message(self, score):
        # A dictionary/list mapping thresholds to messages
        score_ranges = [
            (6000, "Perfecto!"),
            (5000, "You're a pro!"),
            (4000, "Great job!"),
            (3000, "Good effort!"),
            (1000, "No pain, no gain!")
        ]

        for threshold, message in score_ranges:
            if score >= threshold:
                return message
        return "Keep practicing!"

    async def show_scoreboard(self):
        # Clear UI for scoreboard
        while len(self.ui_group) > 0:
            self.ui_group.pop()

        # Add Background
        color_bitmap = displayio.Bitmap(320, 240, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = self.config.color_data.bg_color
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self.ui_group.append(bg_sprite)

        title_label = label.Label(
            terminalio.FONT,
            text="Your Score",
            color=self.config.color_data.fg_color,
            scale=3,
        )
        title_label.anchor_point = (0.5, 0.5)
        title_label.anchored_position = (160, 60)
        self.ui_group.append(title_label)

        score_value_label = label.Label(
            terminalio.FONT,
            text=str(self.total_score),
            color=0xFFFF00,  # Yellow highlight
            scale=4,
        )
        score_value_label.anchor_point = (0.5, 0.5)
        score_value_label.anchored_position = (160, 120)
        self.ui_group.append(score_value_label)

        msg_label = label.Label(
            terminalio.FONT,
            text=self.get_score_message(self.total_score),
            color=self.config.color_data.fg_color,
            scale=2,
        )
        msg_label.anchor_point = (0.5, 0.5)
        msg_label.anchored_position = (160, 180)
        self.ui_group.append(msg_label)

        # Wait for the user to press SELECT to exit
        while self.is_running:
            self.hw.update_button_states()
            if Buttons.L_SELECT.just_pressed:
                self.is_running = False
                break
            await asyncio.sleep(0.01)

    async def animate_score_text(self):
        flash_color = 0xFFA500
        flash_scale = 3
        original_color = self.config.color_data.fg_color
        original_scale = self.score_label.scale

        for _ in range(4):
            self.score_label.color = flash_color
            self.score_label.scale = flash_scale
            await asyncio.sleep(0.1)
            self.score_label.color = original_color
            self.score_label.scale = original_scale
            await asyncio.sleep(0.1)

    def draw_drill_note(self, note):
        self.drill_note_sprite.y = note.staff_y_coord
        self.decorate_note(note, self.drill_note_sprite, self.drill_sharp_sprite, self.drill_flat_sprite, self.drill_c_ledger_line, self.drill_a_ledger_line, self.drill_high_c_ledger_line, self.drill_e_ledger_line)