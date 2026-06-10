import asyncio
import random
import time

import displayio
import gifio
import terminalio
from adafruit_display_text import label

from composer.key_signature import KeySignatures
from composer.notes import Duration, Notes as ComposerNotes, Rest, TimedNote
from composer.note_label import NoteNameLabel
from composer.staff import Staff
from data.config import Config, DrillConfig
from hardware.buttons import Buttons
from hardware.metronome import Metronome
from states.play_state import PlayState


_DURATION_BY_NAME = {
    "WHOLE":   Duration.WHOLE,
    "HALF":    Duration.HALF,
    "QUARTER": Duration.QUARTER,
    "EIGHTH":  Duration.EIGHTH,
}

def parse_drill_item(name):
    """
    Parses a drill-payload string into a TimedNote or Rest.

    "REST"          -> quarter rest (bare REST defaults to quarter, like notes do)
    "REST:HALF"     -> half rest (also accepts REST:WHOLE / REST:QUARTER / REST:EIGHTH)
    "C_4"           -> TimedNote at quarter (default)
    "C_4:HALF"      -> TimedNote at the named duration (WHOLE/HALF/QUARTER/EIGHTH)
    Returns None for unknown names or unknown durations.
    """
    if name == "REST":
        return Rest(Duration.QUARTER)
    if name.startswith("REST:"):
        rest_duration = _DURATION_BY_NAME.get(name[len("REST:"):])
        return Rest(rest_duration) if rest_duration is not None else None

    note_name = name
    duration = Duration.QUARTER
    if ":" in name:
        note_name, _, duration_token = name.partition(":")
        duration = _DURATION_BY_NAME.get(duration_token)
        if duration is None:
            return None

    note = ComposerNotes.get_note_by_name(note_name)
    if note is None:
        return None
    return TimedNote(note, duration)


class ScaleDrillState(PlayState):
    MIN_HOLD = 0.2    # easy-mode floor so fast tempos / eighths don't become twitchy
    LEAD_IN_BEATS = 4  # number of quarter rests prepended in timed mode (1 measure of 4/4)
    PULSE_FLASH_S = 0.15  # how long the mode label stays in the pulse color after a beat

    # Re-export DrillConfig's canonical mode constants so callers within this
    # module don't have to import data.config just to compare a mode value.
    MODE_TIMED = DrillConfig.MODE_TIMED
    MODE_EASY = DrillConfig.MODE_EASY
    # Class-level — persists in-memory across drills within a session, gets
    # re-seeded from config.drill_data.default_mode on boot (see code.py).
    # The ready-phase R_1 toggle and the Drill settings screen both write here.
    SESSION_MODE = MODE_TIMED

    # How many drill items to send to the staff per redraw. The staff
    # width-truncates internally; this just needs to be generous enough that
    # sparse measures (whole notes) leave room for previews of upcoming items.
    DRAW_LOOKAHEAD = 8

    def __init__(self, hardware, payload, config):
        self.drill_name = payload.get("name", "Unknown Drill")
        key_sig_name = payload.get("key_signature", "C_MAJOR")
        self.mode = payload.get("mode", "none")
        key_signature = getattr(KeySignatures, key_sig_name, KeySignatures.C_MAJOR)
        super().__init__(hardware, config, title=self.drill_name, key_signature=key_signature, enable_progress=True)

        self.config = config
        # Payload BPM wins (per-drill override); otherwise fall back to the
        # user's persisted drill default. DrillConfig owns the default value.
        self.bpm = payload.get("bpm", config.drill_data.default_bpm)
        # Scoring attributes
        self.total_score = 0
        self.note_start_time = None
        self.note_played_time = None
        self.MAX_POSSIBLE_PER_NOTE = 5.0  # Placeholder constant
        self.MAX_POSSIBLE_SCORE = 10000

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

        # Mode label sits directly under the drill name (title is at y=15 in
        # PlayState). Doubles as the metronome pulse indicator in timed mode —
        # color flashes on each beat.
        self.mode_label = label.Label(
            terminalio.FONT,
            text=self._mode_label_text(),
            color=config.color_data.fg_color,
            scale=1,
        )
        self.mode_label.anchor_point = (0.0, 0.0)
        self.mode_label.anchored_position = (10, 28)
        self.ui_group.append(self.mode_label)

        # Target-note name in the empty band below the staff lines (the staff
        # group spans the full height but never draws notes this low). Updated
        # from draw_drill_note as the drill advances.
        self.note_name_label = NoteNameLabel(
            color=config.color_data.drill_note_color,
            center_x=PlayState.STAFF_WIDTH // 2,
            top_y=178,
        )
        self.ui_group.append(self.note_name_label)

        # Ready-phase prompts (two lines below the staff). Removed once the
        # drill starts. fingering_color makes them visually distinct from the
        # default fg_color used by every other on-screen element.
        self.ready_prompt_select = label.Label(
            terminalio.FONT,
            text="SELECT: start",
            color=config.color_data.fingering_color,
            scale=1,
        )
        self.ready_prompt_select.anchor_point = (0.5, 0.5)
        self.ready_prompt_select.anchored_position = (160, 210)
        self.ui_group.append(self.ready_prompt_select)

        self.ready_prompt_toggle = label.Label(
            terminalio.FONT,
            text="R1: toggle mode",
            color=config.color_data.fingering_color,
            scale=1,
        )
        self.ready_prompt_toggle.anchor_point = (0.5, 0.5)
        self.ready_prompt_toggle.anchored_position = (160, 226)
        self.ui_group.append(self.ready_prompt_toggle)

        # Metronome — constructed lazily when timed mode actually starts.
        self.metronome = None

        # Timed-mode bookkeeping. current_item_start_time is the wall-clock
        # anchor for the current drill item; the next item's anchor is just
        # this + musical_duration, which keeps the grid drift-free relative
        # to the metronome. _timed_satisfied_seconds is the cumulative time
        # the user has satisfied the current item — scoring is proportional
        # to satisfied_seconds / musical_duration. _timed_satisfied_since is
        # the start of the current in-progress satisfaction streak (None
        # when not currently satisfying).
        self.current_item_start_time = None
        self._timed_satisfied_seconds = 0.0
        self._timed_satisfied_since = None
        # Number of pre-roll rests inserted before the user's drill. These
        # items still tick by the metronome but don't contribute to scoring;
        # see the timed-advance block where score awarding is gated on
        # drill_index >= self.lead_in_count.
        self.lead_in_count = 0

        item_names = payload.get("notes", [])
        self.notes = [parse_drill_item(name) for name in item_names]
        self.notes = [item for item in self.notes if item is not None]

        items_to_add = []
        if self.mode == "rand" or self.mode == "revrand":
            # CircuitPython has no random.sample/choices — use random.choice per slot.
            # Picks with replacement, so the same item can repeat freely.
            items_to_add += [random.choice(self.notes) for _ in range(len(self.notes))]
        if self.mode == "reverse" or self.mode == "revrand":
            items_to_add += list(reversed(self.notes))
            items_to_add.pop(0)

        self.notes += items_to_add

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

    def musical_duration_for(self, item):
        """Seconds the item occupies musically — the fill grows to 100% over
        this duration, matching the metronome's beat timeline."""
        return (60.0 / self.bpm) * Duration.BEATS[item.duration]

    def required_hold_for(self, item):
        """Seconds the player must hold (or rest) to advance past this item.
        Slightly less than the musical duration (hold_factor) so they can drop
        off the last sliver of the note without penalty. MIN_HOLD is a floor
        for very fast tempos / eighths so it doesn't get twitchy."""
        seconds = self.musical_duration_for(item) * self.config.drill_data.hold_factor
        return max(seconds, self.MIN_HOLD)

    def _item_satisfied(self, item, target_note, breathing):
        """A TimedNote is satisfied by playing it with breath; a Rest by not playing."""
        if isinstance(item, Rest):
            return not breathing
        return target_note == item.note and breathing

    def _mode_label_text(self):
        return "[TIMED]" if ScaleDrillState.SESSION_MODE == self.MODE_TIMED else "[EASY]"

    def _on_beat(self, beat_time):
        """Single entry point for everything that happens on a metronome beat.
        Called from Metronome's internal task — synchronous, runs after the
        click fires.

        Today: spawn the visual pulse flash. Coming next: drive drill_index
        advancement and per-note scoring in strict-timing mode. Adding those
        is a new branch here, not a new polling loop somewhere else."""
        asyncio.create_task(self._flash_pulse())

    async def _flash_pulse(self):
        """Briefly recolor the mode label so the user sees the beat. Run as a
        task so it doesn't block the metronome's beat loop."""
        self.mode_label.color = self.config.color_data.drill_note_color
        await asyncio.sleep(self.PULSE_FLASH_S)
        self.mode_label.color = self.config.color_data.fg_color

    async def _ready_phase(self):
        """Pre-drill: clean screen with just title, mode indicator, and prompts.
        Waits for SELECT to start or R_1 to toggle mode. The staff, drill notes,
        and fingering chart all stay hidden until the drill actually begins."""
        if self.hw.display.root_group != self.ui_group:
            self.hw.display.root_group = self.ui_group

        # Hide the staves so the ready screen doesn't show notes or a clef.
        self.staff.hidden = True
        self.drill_staff.hidden = True
        # chart_sprite isn't in ui_group yet — it gets added after ready phase.

        self.hw.display.refresh()

        while self.is_running:
            self.hw.update_button_states()

            if Buttons.L_SELECT.just_pressed:
                break
            if Buttons.R_1.just_pressed:
                ScaleDrillState.SESSION_MODE = (
                    self.MODE_EASY if ScaleDrillState.SESSION_MODE == self.MODE_TIMED
                    else self.MODE_TIMED
                )
                self.mode_label.text = self._mode_label_text()
                self.hw.display.refresh()

            await asyncio.sleep(0.01)

        # Restore visibility and tear down the ready-only prompts.
        self.staff.hidden = False
        self.drill_staff.hidden = False
        if self.ready_prompt_select in self.ui_group:
            self.ui_group.remove(self.ready_prompt_select)
        if self.ready_prompt_toggle in self.ui_group:
            self.ui_group.remove(self.ready_prompt_toggle)
        self.hw.display.refresh()

    async def run(self):
        await self._ready_phase()
        if not self.is_running:
            return

        # Timed-mode setup: prepend lead-in rests so the user has a count-in,
        # then start the metronome. Recompute the score multiplier because
        # len(self.notes) just grew.
        if ScaleDrillState.SESSION_MODE == self.MODE_TIMED:
            lead_in = [Rest(Duration.QUARTER) for _ in range(self.LEAD_IN_BEATS)]
            self.notes = lead_in + self.notes
            self.lead_in_count = self.LEAD_IN_BEATS
            self.SCORE_MULTIPLY_CONSTANT = (
                self.MAX_POSSIBLE_SCORE / (len(self.notes) * self.MAX_POSSIBLE_PER_NOTE) * 1.004
            )
            self.metronome = Metronome(self.hw, on_beat=self._on_beat)
            # Anchor the first item to the same monotonic instant the metronome
            # starts at — beat boundaries and item boundaries then share a grid.
            self.current_item_start_time = time.monotonic()
            self.metronome.start(self.bpm)

        drill_index = 0
        last_drawn_index = -1
        self.note_start_time = time.monotonic()

        if self.chart_sprite not in self.ui_group:
            self.ui_group.append(self.chart_sprite)

        while self.is_running:
            if self.hw.display.root_group != self.ui_group:
                self.hw.display.root_group = self.ui_group

            self.hw.update_button_states()

            if Buttons.L_SELECT.just_pressed or drill_index == len(self.notes):
                # exit if select button pressed or finished
                break

            current_item = self.notes[drill_index]
            musical_duration = self.musical_duration_for(current_item)
            # Timed mode skips MIN_HOLD: the beat ticks regardless of the user,
            # so there's no twitchy-advance concern at fast tempos. Without
            # this, MIN_HOLD could push required_hold above musical_duration
            # for short items and the fill would never reach 100%.
            if ScaleDrillState.SESSION_MODE == self.MODE_TIMED:
                required_hold = musical_duration * self.config.drill_data.hold_factor
            else:
                required_hold = self.required_hold_for(current_item)

            if drill_index != last_drawn_index:
                self.draw_drill_note(drill_index, self.DRAW_LOOKAHEAD)
                self.hw.display.refresh()
                last_drawn_index = drill_index

            # show playing note — match the current drill item's duration so
            # the played note silhouette aligns with (and lines up under) the
            # drill note's column. Rests have no playable note; fall back to
            # quarter for the played sprite in that case.
            target_note = self.hw.get_current_note()
            play_duration = current_item.duration if isinstance(current_item, TimedNote) else Duration.QUARTER
            await self.process_playing_note(target_note, play_duration)

            breathing = self.hw.breath_sensor.breath_sensor_triggered
            current_time = time.monotonic()

            satisfied_now = self._item_satisfied(current_item, target_note, breathing)

            if ScaleDrillState.SESSION_MODE == self.MODE_TIMED:
                # Track cumulative satisfied time as opening/closing streaks.
                if satisfied_now:
                    if self._timed_satisfied_since is None:
                        self._timed_satisfied_since = current_time
                else:
                    if self._timed_satisfied_since is not None:
                        self._timed_satisfied_seconds += current_time - self._timed_satisfied_since
                        self._timed_satisfied_since = None

                # Fill represents satisfied seconds (not wall-clock) so wrong
                # notes never appear to make progress. The beat boundary still
                # advances on musical_duration regardless of satisfaction.
                satisfied_so_far = self._timed_satisfied_seconds
                if self._timed_satisfied_since is not None:
                    satisfied_so_far += current_time - self._timed_satisfied_since
                self.staff.set_progress(satisfied_so_far / required_hold)

                elapsed_in_item = current_time - self.current_item_start_time

                if elapsed_in_item >= musical_duration:
                    # Close any in-progress streak at the item boundary so it
                    # doesn't leak into the next item. If they're still
                    # holding, the streak picks up from the boundary instant
                    # against the next item's window.
                    item_end = self.current_item_start_time + musical_duration
                    if self._timed_satisfied_since is not None:
                        self._timed_satisfied_seconds += item_end - self._timed_satisfied_since
                        self._timed_satisfied_since = item_end
                    # Score caps at required_hold, not musical_duration — playing
                    # the required_hold window earns a full slice; the remaining
                    # ~20% of the beat is breathing room and doesn't penalize.
                    # Lead-in rests are part of the count-in, not the drill, so
                    # they're excluded from both the slice size and the award.
                    if drill_index >= self.lead_in_count:
                        scored_count = len(self.notes) - self.lead_in_count
                        satisfied_fraction = min(1.0, self._timed_satisfied_seconds / required_hold)
                        slice_max = int(self.MAX_POSSIBLE_SCORE / scored_count)
                        slice_score = int(slice_max * satisfied_fraction)
                        if slice_score > 0:
                            self.total_score += slice_score
                            self.score_label.text = str(self.total_score)

                    if self.hint_task is not None:
                        self.hint_task.cancel()
                        self.hint_task = None
                    if self.current_hint_fingering is not None:
                        await self.clear_specific_fingering(self.current_hint_fingering)
                        self.current_hint_fingering = None

                    # Keep the next item's anchor on the same grid as the
                    # metronome by adding musical_duration — using monotonic()
                    # here would let drift creep in.
                    drill_index += 1
                    self.current_item_start_time += musical_duration
                    self._timed_satisfied_seconds = 0.0
                    self.note_start_time = time.monotonic()
                    self.note_played_time = None
                    # Skip animate_score_text in timed mode — it blocks the
                    # timeline. Score updates in-place via score_label.
            else:
                # Easy mode: event-driven advance based on hold satisfaction.
                if satisfied_now:
                    if self.note_played_time is None:
                        self.note_played_time = current_time
                else:
                    if self.note_played_time is not None:
                        self.note_played_time = None

                # Fill reaches 100% at required_hold so the visual cue and the
                # advance threshold match — when the note looks done, it is done.
                if self.note_played_time is not None:
                    self.staff.set_progress((current_time - self.note_played_time) / required_hold)
                else:
                    self.staff.set_progress(0.0)

                if self.note_played_time is not None and current_time - self.note_played_time >= required_hold:
                    if self.note_start_time is None:
                        self.note_start_time = self.note_played_time

                    reaction_time = self.note_played_time - self.note_start_time
                    score = int( (max(0.0, self.MAX_POSSIBLE_PER_NOTE - reaction_time) * self.SCORE_MULTIPLY_CONSTANT) )
                    score = int( score * (1.1 if drill_index == 0 else 1))
                    score = min(score, int(self.MAX_POSSIBLE_SCORE/len(self.notes)))
                    self.total_score += score
                    self.score_label.text = str(self.total_score)

                    print(f"Success! Score awarded: {score}")

                    if self.hint_task is not None:
                        self.hint_task.cancel()
                        self.hint_task = None
                    if self.current_hint_fingering is not None:
                        await self.clear_specific_fingering(self.current_hint_fingering)
                        self.current_hint_fingering = None

                    await self.animate_score_text()

                    drill_index += 1
                    self.note_start_time = time.monotonic()
                    self.note_played_time = None
                    print(f"Moving to next item. Total score so far: {self.total_score}")

            # 3. HINT: Show fingering. Timed mode shows it immediately on each
            #    item — the player is racing the beat and shouldn't have to
            #    earn the hint. Easy mode keeps the "taking too long" timeout
            #    so it stays a soft assist. Rests have no fingering to hint.
            #    Re-read from self.notes — the advance blocks above may have
            #    just bumped drill_index, leaving the loop-top current_item
            #    stale. (Easy mode's MAX-2 gate masks this; timed mode would
            #    otherwise kick off a hint for the previous note here.)
            if drill_index < len(self.notes):
                hint_item = self.notes[drill_index]
                if (self.hint_task is None
                        and self.note_start_time is not None
                        and isinstance(hint_item, TimedNote)
                        and (ScaleDrillState.SESSION_MODE == self.MODE_TIMED
                             or time.monotonic() - self.note_start_time > self.MAX_POSSIBLE_PER_NOTE - 2)):
                    self.hint_task = asyncio.create_task(self.cycle_fingerings(hint_item.note))

            # No beat-related polling here — beat-driven side effects (visual
            # pulse, and eventually drill advancement) all flow through the
            # metronome's on_beat hook, dispatched by self._on_beat.

            # yield control for other code to run
            await asyncio.sleep(0.001)

        if self.metronome is not None:
            self.metronome.stop()

        # Cancel any leftover hint tasks upon exiting
        if self.hint_task is not None:
            self.hint_task.cancel()
            
        if self.current_hint_fingering is not None:
            await self.clear_specific_fingering(self.current_hint_fingering)
            self.current_hint_fingering = None

        await self.hw.stop_note()

        if drill_index == len(self.notes):
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

    def draw_drill_note(self, first_index, count):
        items_to_show = self.notes[first_index:min(first_index + count, len(self.notes))]
        # Musical-beat position of the first visible item; Staff uses it to
        # place measure lines correctly as the window scrolls past barlines.
        start_beat = 0.0
        for i in range(first_index):
            start_beat += Duration.BEATS.get(self.notes[i].duration, 1.0)
        self.drill_staff.update_sequence(items_to_show)
        # Measure lines render on the base staff (not drill_staff) so they
        # share the staff-line color source. drill_staff's fg_color is
        # overridden to drill_note_color; the base staff is unmodified.
        self.staff.set_measure_lines(items_to_show, start_beat=start_beat)
        # Name the current target (first visible item). Rests have no .note,
        # so the label clears itself during rests and the lead-in.
        target = items_to_show[0] if items_to_show else None
        self.note_name_label.set_note_name(getattr(getattr(target, "note", None), "name", None))