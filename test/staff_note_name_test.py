import sys
import os
import displayio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from composer.staff import Staff
from composer.notes import Notes, TimedNote, Duration
from composer.note_label import NoteNameLabel
from composer.key_signature import KeySignatures
from display_utils import prep_display, show_and_wait
from data.config import Config

STAFF_WIDTH = 212
# Empty band below the staff lines, mirroring ScaleDrillState's placement.
NAME_TOP_Y = 178


def _scene(config, display, note, key_sig=None):
    """Draws a staff with `note` on it plus the NoteNameLabel below, so the
    label can be eyeballed against the rendered note."""
    staff = Staff(width=STAFF_WIDTH, config=config, key_signature=key_sig or KeySignatures.C_MAJOR)
    staff.y = (display.height - Staff.HEIGHT) // 2
    display.root_group.append(staff)
    staff.update_sequence([TimedNote(note, Duration.QUARTER)])

    name_label = NoteNameLabel(
        color=config.color_data.drill_note_color,
        center_x=STAFF_WIDTH // 2,
        top_y=NAME_TOP_Y,
    )
    name_label.set_note_name(note.name)
    display.root_group.append(name_label)
    return staff, name_label


def test_natural():
    """Plain letter + superscript octave, e.g. C with a small 4."""
    config = Config()
    display = prep_display(config=config, height=240)
    _scene(config, display, Notes.C_4)
    show_and_wait(display)


def test_sharp():
    """Sharp accidental in the name: F# with a small 4."""
    config = Config()
    display = prep_display(config=config, height=240)
    _scene(config, display, Notes.F_SHARP_4)
    show_and_wait(display)


def test_flat():
    """Flat accidental and a lower octave: Bb with a small 3."""
    config = Config()
    display = prep_display(config=config, height=240)
    _scene(config, display, Notes.B_FLAT_3)
    show_and_wait(display)


def test_high_octave():
    """Octave 5/6 superscript reads correctly."""
    config = Config()
    display = prep_display(config=config, height=240)
    _scene(config, display, Notes.A_5)
    show_and_wait(display)


def test_cycle():
    """One label updated through a range of notes — checks centering holds as
    the text width changes (1 char vs 2, octave digit changes)."""
    import pygame
    import time

    config = Config()
    display = prep_display(config=config, height=240)
    staff, name_label = _scene(config, display, Notes.C_4)

    notes = [
        Notes.C_4, Notes.E_4, Notes.G_4, Notes.B_FLAT_4,
        Notes.C_5, Notes.F_SHARP_5, Notes.A_5, Notes.C_6,
    ]

    print("Cycling note names — close the window or press Ctrl+C to stop.")
    i = 0
    last_switch = time.monotonic()
    HOLD_SECONDS = 1.0

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            now = time.monotonic()
            if now - last_switch >= HOLD_SECONDS:
                note = notes[i % len(notes)]
                staff.update_sequence([TimedNote(note, Duration.QUARTER)])
                name_label.set_note_name(note.name)
                print(f"  {note.name}")
                i += 1
                last_switch = now

            display.refresh()
            time.sleep(0.01)
    except KeyboardInterrupt:
        pygame.quit()


TESTS = {
    "natural": test_natural,
    "sharp":   test_sharp,
    "flat":    test_flat,
    "high":    test_high_octave,
    "cycle":   test_cycle,
}

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "natural"
    TESTS[name]()