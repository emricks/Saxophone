import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from composer.staff import Staff
from composer.notes import Notes, TimedNote, Duration
from composer.key_signature import KeySignatures
from display_utils import prep_display
from data.config import Config


def _make_staff(config, display, enable_progress=False, key_sig=None):
    staff = Staff(
        width=212,
        config=config,
        key_signature=key_sig or KeySignatures.C_MAJOR,
        enable_progress=enable_progress,
    )
    staff.y = (display.height - Staff.HEIGHT) // 2
    display.root_group.append(staff)
    return staff


def _animate_progress(display, on_tick, cycle_seconds=3.0):
    """Calls on_tick(fraction, cycle_index) on every frame; fraction ramps 0->1 over
    cycle_seconds and resets, with cycle_index incrementing each loop."""
    import pygame
    cycle_start = time.monotonic()
    cycle_index = 0
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            now = time.monotonic()
            elapsed = now - cycle_start
            if elapsed >= cycle_seconds:
                cycle_index += 1
                cycle_start = now
                elapsed = 0.0
            fraction = elapsed / cycle_seconds
            on_tick(fraction, cycle_index)
            display.refresh()
            time.sleep(0.02)
    except KeyboardInterrupt:
        pygame.quit()


def test_progress_cycle():
    """Single quarter note, fill ramps 0->1 repeatedly."""
    config = Config()
    display = prep_display(config=config)
    staff = _make_staff(config, display, enable_progress=True)
    staff.show_note(Notes.B_4, Duration.QUARTER)

    def tick(fraction, _):
        staff.set_progress(fraction)

    _animate_progress(display, tick, cycle_seconds=3.0)


def test_progress_each_duration():
    """Cycles through whole/half/quarter/eighth, each filling 0->1."""
    config = Config()
    display = prep_display(config=config)
    staff = _make_staff(config, display, enable_progress=True)

    sequence = [
        (Notes.B_4, Duration.WHOLE),
        (Notes.B_4, Duration.HALF),
        (Notes.B_4, Duration.QUARTER),
        (Notes.B_4, Duration.EIGHTH),
    ]
    state = {"last_cycle": -1}
    note, duration = sequence[0]
    staff.show_note(note, duration)

    def tick(fraction, cycle_index):
        if cycle_index != state["last_cycle"]:
            n, d = sequence[cycle_index % len(sequence)]
            staff.show_note(n, d)
            state["last_cycle"] = cycle_index
        staff.set_progress(fraction)

    _animate_progress(display, tick, cycle_seconds=2.5)


def test_progress_with_drill_overlay():
    """Mimics drill mode: drill staff (drill color) behind, play staff (fg color, fill) on top."""
    config = Config()
    display = prep_display(config=config)

    drill_config = Config()
    drill_config.color_data.fg_color = config.color_data.drill_note_color
    drill_staff = Staff(width=212, config=drill_config, key_signature=KeySignatures.C_MAJOR)
    drill_staff.y = (display.height - Staff.HEIGHT) // 2
    while len(drill_staff.static_group) > 0:
        drill_staff.static_group.pop()
    display.root_group.append(drill_staff)
    drill_staff.update_sequence([TimedNote(Notes.B_4, Duration.QUARTER)])

    play_staff = Staff(
        width=212,
        config=config,
        key_signature=KeySignatures.C_MAJOR,
        enable_progress=True,
    )
    play_staff.y = drill_staff.y
    display.root_group.append(play_staff)
    play_staff.show_note(Notes.B_4, Duration.QUARTER)

    def tick(fraction, _):
        play_staff.set_progress(fraction)

    _animate_progress(display, tick, cycle_seconds=2.5)


TESTS = {
    "cycle":     test_progress_cycle,
    "durations": test_progress_each_duration,
    "drill":     test_progress_with_drill_overlay,
}

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "cycle"
    TESTS[name]()