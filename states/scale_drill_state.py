import asyncio
import random
import time

import displayio
import gifio
import terminalio
from adafruit_display_text import label

from composer.key_signature import KeySignatures
from composer.notes import Duration, Notes as ComposerNotes, TimedNote
from composer.staff import Staff
from data.config import Config
from hardware.buttons import Buttons
from states.play_state import PlayState


class ScaleDrillState(PlayState):
    def __init__(self, hardware, payload, config):
        self.drill_name = payload.get("name", "Unknown Drill")
        key_sig_name = payload.get("key_signature", "C_MAJOR")
        self.mode = payload.get("mode", "rand")
        key_signature = getattr(KeySignatures, key_sig_name, KeySignatures.C_MAJOR)
        super().__init__(hardware, config, title=self.drill_name, key_signature=key_signature)

        self.config = config
        # Scoring attributes
        self.total_score = 0
        self.note_start_time = None
        self.note_played_time = None
        self.MAX_POSSIBLE_PER_NOTE = 5.0  # Placeholder constant
        self.MAX_POSSIBLE_SCORE = 10000
        self.REQUIRED_HOLD_TIME = 0.5

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
        self.notes = [ComposerNotes.get_note_by_name(name) for name in note_names if ComposerNotes.get_note_by_name(name) is not None]

        notes_to_add = []
        if self.mode == "rand":
            notes_to_add = random.sample(self.notes, len(self.notes))
        elif self.mode == "reverse":
            notes_to_add = list(reversed(self.notes))
            notes_to_add.pop(0)

        self.notes += notes_to_add

        self.SCORE_MULTIPLY_CONSTANT = self.MAX_POSSIBLE_SCORE/(len(self.notes) * self.MAX_POSSIBLE_PER_NOTE) * 1.004

        # Drill note overlay staff (same position as play staff, no lines/clef, drill color)
        drill_config = Config()
        drill_config.color_data.fg_color = config.color_data.drill_note_color
        self.drill_staff = Staff(width=PlayState.STAFF_WIDTH, config=drill_config, key_signature=key_signature)
        self.drill_staff.x = self.staff.x
        self.drill_staff.y = self.staff.y
        while len(self.drill_staff.static_group) > 0:
            self.drill_staff.static_group.pop()
        self.ui_group.insert(1, self.drill_staff)

    async def run(self):
        drill_note_index = 0
        last_drawn_index = -1
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
            if drill_note_index != last_drawn_index:
                self.draw_drill_note(drill_note_index, 3)
                self.hw.display.refresh()
                last_drawn_index = drill_note_index

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
                if current_time - self.note_played_time >= self.REQUIRED_HOLD_TIME:
                    # SUCCESS! Now we calculate and award the score
                    if self.note_start_time is None:
                        self.note_start_time = self.note_played_time

                    reaction_time = self.note_played_time - self.note_start_time
                    score = int( (max(0.0, self.MAX_POSSIBLE_PER_NOTE - reaction_time) * self.SCORE_MULTIPLY_CONSTANT) )
                    score = int( score * (1.1 if drill_note_index == 0 else 1))
                    score = min(score, int(self.MAX_POSSIBLE_SCORE/len(self.notes)))
                    self.total_score += score
                    self.score_label.text = str(self.total_score)

                    print(f"Success! Score awarded: {score}")

                    # Cancel hint cycle if it's running
                    if self.hint_task is not None:
                        self.hint_task.cancel()
                        self.hint_task = None

                    if self.current_hint_fingering is not None:
                        await self.clear_specific_fingering(self.current_hint_fingering)
                        self.current_hint_fingering = None

                    # Animate score flash, then advance — sequential keeps display updates isolated
                    await self.animate_score_text()

                    # Move to next note and reset state
                    drill_note_index += 1
                    self.note_start_time = time.monotonic()
                    self.note_played_time = None
                    print(f"Moving to next note. Total score so far: {self.total_score}")
            
            # 3. HINT: If they are taking too long, start cycling the fingerings
            if self.hint_task is None and self.note_start_time is not None:
                if time.monotonic() - self.note_start_time > self.MAX_POSSIBLE_PER_NOTE - 2:
                    self.hint_task = asyncio.create_task(self.cycle_fingerings(current_note))

            # yield control for other code to run
            await asyncio.sleep(0.001)

        # Cancel any leftover hint tasks upon exiting
        if self.hint_task is not None:
            self.hint_task.cancel()
            
        if self.current_hint_fingering is not None:
            await self.clear_specific_fingering(self.current_hint_fingering)
            self.current_hint_fingering = None

        await self.hw.stop_note()

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
        # A dictionary/list mapping thresholds to messages and GIFs
        score_ranges = [
            (8500, {"message": "Perfecto!", "gif": "data/gif/lasercat.gif"}),
            (7500, {"message": "You're a pro!", "gif": "data/gif/groovin.gif"}),
            (6000, {"message": "Great job!", "gif": "data/gif/party.gif"}),
            (4000, {"message": "Good effort!", "gif": "data/gif/meh.gif"}),
            (1500, {"message": "No pain, no gain!", "gif": "data/gif/tough.gif"})
        ]

        for threshold, data in score_ranges:
            if score >= threshold:
                return data
        return {"message": "Keep practicing!", "gif": "data/gif/tough.gif"}

    async def show_scoreboard(self):
        # Clear UI for scoreboard
        while len(self.ui_group) > 0:
            self.ui_group.pop()

        score_data = self.get_score_message(self.total_score)

        # Always add a solid background first
        color_bitmap = displayio.Bitmap(320, 240, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = self.config.color_data.bg_color
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self.ui_group.append(bg_sprite)

        # Add GIF on top of the background, in the middle
        gif_path = score_data["gif"]
        try:
            gif = gifio.OnDiskGif(gif_path)
            gif.next_frame() # Load the first frame
            
            # Center the 100x100 gif horizontally, position vertically between score and message
            screen_w = 320
            x_offset = max(0, (screen_w - gif.width) // 2)
            y_offset = 95
            
            gif_sprite = displayio.TileGrid(
                gif.bitmap,
                pixel_shader=displayio.ColorConverter(
                    input_colorspace=displayio.Colorspace.RGB565_SWAPPED
                ),
                width=1, 
                height=1, 
                tile_width=gif.width, 
                tile_height=gif.height,
                x=x_offset,
                y=y_offset
            )
            self.ui_group.append(gif_sprite)
        except Exception as e:
            print(f"Could not load GIF {gif_path}: {e}")
            gif = None

        title_label = label.Label(
            terminalio.FONT,
            text="Your Score",
            color=self.config.color_data.fg_color,
            scale=3,
        )
        title_label.anchor_point = (0.5, 0.5)
        title_label.anchored_position = (160, 30)
        self.ui_group.append(title_label)

        score_value_label = label.Label(
            terminalio.FONT,
            text=str(self.total_score),
            color=0xFFFF00,  # Yellow highlight
            scale=4,
        )
        score_value_label.anchor_point = (0.5, 0.5)
        score_value_label.anchored_position = (160, 65)
        self.ui_group.append(score_value_label)

        msg_label = label.Label(
            terminalio.FONT,
            text=score_data["message"],
            color=self.config.color_data.fg_color,
            scale=2,
        )
        msg_label.anchor_point = (0.5, 0.5)
        msg_label.anchored_position = (160, 215)
        self.ui_group.append(msg_label)

        # Wait for the user to press SELECT to exit
        while self.is_running:
            self.hw.update_button_states()
            if Buttons.L_SELECT.just_pressed:
                self.is_running = False
                break
            
            if gif is not None:
                gif.next_frame()

            await asyncio.sleep(0.01)

    async def animate_score_text(self):
        flash_color = 0xFFA500
        flash_scale = 3
        original_color = self.config.color_data.fg_color
        original_scale = self.score_label.scale

        for _ in range(3):
            self.score_label.color = flash_color
            self.score_label.scale = flash_scale
            self.hw.display.refresh()
            await asyncio.sleep(0.05)
            self.score_label.color = original_color
            self.score_label.scale = original_scale
            self.hw.display.refresh()
            await asyncio.sleep(0.05)

    def draw_drill_note(self, first_note_index, number_of_notes):
        notes_to_show = self.notes[first_note_index:min(first_note_index+number_of_notes, len(self.notes))]
        self.drill_staff.update_sequence([TimedNote(note, Duration.QUARTER) for note in notes_to_show])