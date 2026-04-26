import sys
import os
import displayio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from composer.staff import Staff
from composer.notes import Notes, TimedNote, Duration
from composer.key_signature import KeySignatures
from display_utils import prep_display, show_and_wait
from data.config import Config


def _make_staff(config, display, key_sig=None):
    staff = Staff(width=212, config=config, key_signature=key_sig or KeySignatures.C_MAJOR)
    staff.y = (display.height - Staff.HEIGHT) // 2
    display.root_group.append(staff)
    return staff


def test_whole_note():
    """Single whole note — should be centered horizontally in the measure."""
    config = Config()
    display = prep_display(config=config)
    staff = _make_staff(config, display)
    staff.update_sequence([TimedNote(Notes.B_4, Duration.WHOLE)])
    show_and_wait(display)


def test_two_half_notes():
    """Two half notes filling a 4/4 measure — each centered in its half."""
    config = Config()
    display = prep_display(config=config)
    staff = _make_staff(config, display)
    staff.update_sequence([
        TimedNote(Notes.E_4, Duration.HALF),
        TimedNote(Notes.G_4, Duration.HALF),
    ])
    show_and_wait(display)


def test_four_quarter_notes():
    """Four quarter notes — evenly spaced across the measure."""
    config = Config()
    display = prep_display(config=config)
    staff = _make_staff(config, display)
    staff.update_sequence([
        TimedNote(Notes.C_4,  Duration.QUARTER),
        TimedNote(Notes.E_4,  Duration.QUARTER),
        TimedNote(Notes.G_4,  Duration.QUARTER),
        TimedNote(Notes.C_5,  Duration.QUARTER),
    ])
    show_and_wait(display)


def test_mixed_durations():
    """Half + two quarters = 4 beats."""
    config = Config()
    display = prep_display(config=config)
    staff = _make_staff(config, display)
    staff.update_sequence([
        TimedNote(Notes.G_4,  Duration.HALF),
        TimedNote(Notes.E_4,  Duration.QUARTER),
        TimedNote(Notes.D_4,  Duration.QUARTER),
    ])
    show_and_wait(display)


def test_key_sig_sharps():
    """G major: F# covered by key sig (no decoration), F natural gets natural sign."""
    config = Config()
    display = prep_display(config=config)
    staff = _make_staff(config, display, key_sig=KeySignatures.G_MAJOR)
    staff.update_sequence([
        TimedNote(Notes.F_SHARP_4, Duration.QUARTER),  # no decoration
        TimedNote(Notes.F_4,       Duration.QUARTER),  # natural sign
        TimedNote(Notes.G_4,       Duration.QUARTER),
        TimedNote(Notes.A_4,       Duration.QUARTER),
    ])
    show_and_wait(display)


def test_key_sig_flats():
    """Bb major: Bb covered, B natural gets natural sign."""
    config = Config()
    display = prep_display(config=config)
    staff = _make_staff(config, display, key_sig=KeySignatures.B_FLAT_MAJOR)
    staff.update_sequence([
        TimedNote(Notes.B_FLAT_4, Duration.QUARTER),  # covered
        TimedNote(Notes.B_4,      Duration.QUARTER),  # natural
        TimedNote(Notes.E_FLAT_4, Duration.QUARTER),  # covered
        TimedNote(Notes.C_5,      Duration.QUARTER),
    ])
    show_and_wait(display)


def test_ledger_lines():
    """Notes requiring ledger lines above and below the staff."""
    config = Config()
    display = prep_display(config=config)
    staff = _make_staff(config, display)
    staff.update_sequence([
        TimedNote(Notes.C_4, Duration.QUARTER),   # 1 ledger line below
        TimedNote(Notes.B_3, Duration.QUARTER),   # sits below that ledger line
        TimedNote(Notes.A_5, Duration.QUARTER),   # 1 ledger line above
        TimedNote(Notes.C_6, Duration.QUARTER),   # 2 ledger lines above
    ])
    show_and_wait(display)


def test_update_loop():
    """One staff that cycles through several sequences, pausing between each."""
    import pygame
    import time

    config = Config()
    display = prep_display(config=config)
    staff = _make_staff(config, display)

    sequences = [
        [TimedNote(Notes.C_4,  Duration.WHOLE)],
        [TimedNote(Notes.E_4,  Duration.HALF),  TimedNote(Notes.G_4,  Duration.HALF)],
        [TimedNote(Notes.C_4,  Duration.QUARTER), TimedNote(Notes.E_4, Duration.QUARTER),
         TimedNote(Notes.G_4,  Duration.QUARTER), TimedNote(Notes.C_5, Duration.QUARTER)],
        [TimedNote(Notes.G_4,  Duration.HALF),  TimedNote(Notes.E_4,  Duration.QUARTER),
         TimedNote(Notes.D_4,  Duration.QUARTER)],
        [TimedNote(Notes.B_4,  Duration.WHOLE)],
    ]

    print("Cycling through sequences — close the window or press Ctrl+C to stop.")
    seq_index = 0
    last_switch = time.monotonic()
    HOLD_SECONDS = 1.5

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            now = time.monotonic()
            if now - last_switch >= HOLD_SECONDS:
                staff.update_sequence(sequences[seq_index % len(sequences)])
                print(f"  sequence {seq_index % len(sequences)}")
                seq_index += 1
                last_switch = now

            display.refresh()
            time.sleep(0.01)
    except KeyboardInterrupt:
        pygame.quit()


TESTS = {
    "whole":    test_whole_note,
    "halves":   test_two_half_notes,
    "quarters": test_four_quarter_notes,
    "mixed":    test_mixed_durations,
    "sharps":   test_key_sig_sharps,
    "flats":    test_key_sig_flats,
    "ledger":   test_ledger_lines,
    "loop":     test_update_loop,
}

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "quarters"
    TESTS[name]()