"""Visual sweep for Staff dynamic measure-width layout.

Cycles through scenarios with both update_sequence and set_measure_lines
applied, so notes and barlines are visible together. Run as:

    python test/staff_layout_test.py        # cycles all scenarios
    python test/staff_layout_test.py whole  # one specific scenario
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from composer.staff import Staff
from composer.notes import Notes, TimedNote, Rest, Duration
from composer.key_signature import KeySignatures
from display_utils import prep_display, show_and_wait
from data.config import Config


N = Notes
W, H, Q, E = Duration.WHOLE, Duration.HALF, Duration.QUARTER, Duration.EIGHTH


def tn(note, dur):
    return TimedNote(note, dur)


# Each scenario: (label, items, optional key_sig, optional start_beat)
SCENARIOS = [
    ("1. single whole",
     [tn(N.B_4, W)]),

    ("2. two halves",
     [tn(N.E_4, H), tn(N.G_4, H)]),

    ("3. four quarters",
     [tn(N.C_4, Q), tn(N.E_4, Q), tn(N.G_4, Q), tn(N.C_5, Q)]),

    ("4. eight eighths",
     [tn(N.C_4, E), tn(N.D_4, E), tn(N.E_4, E), tn(N.F_4, E),
      tn(N.G_4, E), tn(N.A_4, E), tn(N.B_4, E), tn(N.C_5, E)]),

    ("5. whole + next-measure preview",
     [tn(N.B_4, W),
      tn(N.C_4, Q), tn(N.E_4, Q), tn(N.G_4, Q), tn(N.C_5, Q)]),

    ("6. half-half | quarter-quarter-quarter-quarter (2 measures)",
     [tn(N.E_4, H), tn(N.G_4, H),
      tn(N.C_4, Q), tn(N.E_4, Q), tn(N.G_4, Q), tn(N.C_5, Q)]),

    ("7. whole | whole (2 measures, sparse-sparse)",
     [tn(N.B_4, W), tn(N.D_5, W)]),

    ("8. quarter*4 | whole (dense-then-sparse)",
     [tn(N.C_4, Q), tn(N.E_4, Q), tn(N.G_4, Q), tn(N.C_5, Q),
      tn(N.E_5, W)]),

    ("9. mixed (quarter + half + quarter + 4 quarters)",
     [tn(N.C_4, Q), tn(N.E_4, H), tn(N.G_4, Q),
      tn(N.C_5, Q), tn(N.B_4, Q), tn(N.A_4, Q), tn(N.G_4, Q)]),

    ("10. ledger lines in dense window",
     [tn(N.C_4, Q), tn(N.B_3, Q), tn(N.A_5, Q), tn(N.C_6, Q),
      tn(N.E_4, Q), tn(N.G_4, Q)]),

    ("11. key sig G major + naturals (dense)",
     [tn(N.F_SHARP_4, Q), tn(N.F_4, Q), tn(N.G_4, Q), tn(N.A_4, Q),
      tn(N.B_4, Q), tn(N.F_SHARP_4, Q)],
     KeySignatures.G_MAJOR),

    ("12. quarter rests mixed with notes",
     [tn(N.C_4, Q), Rest(Q), tn(N.E_4, H),
      tn(N.G_4, Q), Rest(Q), tn(N.C_5, Q)]),

    ("13. whole rest alone (empty measure)",
     [Rest(W)]),

    ("14. half rest + half note | 4 quarter rests",
     [Rest(H), tn(N.G_4, H),
      Rest(Q), Rest(Q), Rest(Q), Rest(Q)]),

    ("15. rest measure | notes measure",
     [Rest(W),
      tn(N.C_4, Q), tn(N.E_4, Q), tn(N.G_4, Q), tn(N.C_5, Q)]),

    ("16. eighth rests + eighth notes (run)",
     [tn(N.C_4, E), Rest(E), tn(N.E_4, E), Rest(E),
      tn(N.G_4, E), Rest(E), tn(N.C_5, E), Rest(E)]),
]


# Scrolling scenario — a long drill, simulating the window advancing.
SCROLL_ITEMS = [
    tn(N.C_4, Q), tn(N.D_4, Q), tn(N.E_4, Q), tn(N.F_4, Q),  # measure 1
    tn(N.G_4, H), tn(N.A_4, H),                              # measure 2
    tn(N.B_4, W),                                            # measure 3
    tn(N.C_5, Q), tn(N.B_4, Q), tn(N.A_4, Q), tn(N.G_4, Q),  # measure 4
    tn(N.F_4, H), tn(N.E_4, Q), tn(N.D_4, Q),                # measure 5
]


def _make_staff(config, display, key_sig=None):
    staff = Staff(width=212, config=config, key_signature=key_sig or KeySignatures.C_MAJOR)
    staff.y = (display.height - Staff.HEIGHT) // 2
    display.root_group.append(staff)
    return staff


def _render(staff, items, start_beat=0.0):
    staff.update_sequence(items)
    staff.set_measure_lines(items, start_beat=start_beat)


def test_scenario_loop():
    """Cycles through every fixed scenario, printing the label so you can
    tell which one is on screen. Close the window or Ctrl+C to exit."""
    import pygame
    config = Config()
    display = prep_display(config=config)

    # Rebuild the staff per scenario so the key signature can change
    # without state carrying over.
    HOLD_SECONDS = 2.0
    print("Scenario sweep — close window or Ctrl+C to stop.")
    print(f"  ({HOLD_SECONDS:.1f}s per scenario)")

    try:
        idx = 0
        while True:
            scenario = SCENARIOS[idx % len(SCENARIOS)]
            label = scenario[0]
            items = scenario[1]
            key_sig = scenario[2] if len(scenario) > 2 else None

            # Tear down and rebuild
            while len(display.root_group) > 1:  # keep the bg sprite
                display.root_group.pop()
            staff = _make_staff(config, display, key_sig=key_sig)
            _render(staff, items)
            print(f"  [{idx % len(SCENARIOS):2d}] {label}")

            start = time.monotonic()
            while time.monotonic() - start < HOLD_SECONDS:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                display.refresh()
                time.sleep(0.01)
            idx += 1
    except KeyboardInterrupt:
        pygame.quit()


def _run_scroll(items, key_sig, label):
    """Shared scroll harness — walks an 8-wide window through `items` one
    step per tick, redrawing notes + measure lines each step."""
    import pygame
    config = Config()
    display = prep_display(config=config)
    staff = _make_staff(config, display, key_sig=key_sig)

    LOOKAHEAD = 8
    HOLD_SECONDS = 1.2
    print(f"{label} — {len(items)} items, window of {LOOKAHEAD}, {HOLD_SECONDS:.1f}s per tick.")

    try:
        for first in range(len(items)):
            window = items[first:first + LOOKAHEAD]
            start_beat = 0.0
            for i in range(first):
                start_beat += Duration.BEATS[items[i].duration]
            _render(staff, window, start_beat=start_beat)
            print(f"  first={first:2d}  start_beat={start_beat:5.1f}")

            start = time.monotonic()
            while time.monotonic() - start < HOLD_SECONDS:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                display.refresh()
                time.sleep(0.01)
    except KeyboardInterrupt:
        pygame.quit()


def test_scroll():
    """Scroll through SCROLL_ITEMS in C major. Verifies measure lines stay
    anchored to musical beats as items drop off the left."""
    _run_scroll(SCROLL_ITEMS, KeySignatures.C_MAJOR, "Scroll sweep (C major)")


# Big-key scroll: every accidental that the key sig declares natural-by-default
# (Cb-major, 7 flats) gets a flat decoration; explicit naturals appear when a
# plain letter shows up. Squeezes the available width to its tightest case.
BIG_KEY_SCROLL_ITEMS = [
    tn(N.B_FLAT_4, Q), tn(N.E_FLAT_4, Q), tn(N.A_FLAT_4, Q), tn(N.D_FLAT_4, Q),  # measure 1
    tn(N.G_FLAT_4, H), tn(N.C_FLAT_4, H),                                         # measure 2
    tn(N.F_FLAT_4, W),                                                            # measure 3
    tn(N.B_4, Q), tn(N.E_4, Q), tn(N.A_4, Q), tn(N.D_4, Q),                       # measure 4 (all naturals)
    Rest(H), tn(N.G_FLAT_4, H),                                                   # measure 5
]


def test_scroll_big_key():
    """Scroll through a 7-flat key signature (Cb major). Demonstrates layout
    behavior when the key sig eats most of the horizontal budget."""
    _run_scroll(BIG_KEY_SCROLL_ITEMS, KeySignatures.C_FLAT_MAJOR, "Scroll sweep (Cb major, 7 flats)")


def test_single(name):
    """Renders one named scenario and waits. Use the 1-based label number
    shown by the loop (e.g. "13" picks scenario "13. whole rest alone")."""
    config = Config()
    display = prep_display(config=config)
    idx = int(name) - 1
    scenario = SCENARIOS[idx]
    label = scenario[0]
    items = scenario[1]
    key_sig = scenario[2] if len(scenario) > 2 else None
    staff = _make_staff(config, display, key_sig=key_sig)
    _render(staff, items)
    print(f"Showing: {label}")
    show_and_wait(display)


TESTS = {
    "loop":       test_scenario_loop,
    "scroll":     test_scroll,
    "scroll_big": test_scroll_big_key,
}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        test_single(sys.argv[1])
    else:
        name = sys.argv[1] if len(sys.argv) > 1 else "loop"
        TESTS[name]()
