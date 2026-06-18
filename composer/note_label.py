import displayio
import terminalio
from adafruit_display_text import label

from composer.notes import Accidental, display_parts

# terminalio.FONT has no proper sharp/flat glyphs, so fall back to ASCII.
_ACC_SYMBOL = {
    Accidental.FLAT: "b",
    Accidental.SHARP: "#",
    Accidental.NATURAL: "",
}


class NoteNameLabel(displayio.Group):
    """The name of a note as a large pitch letter (plus accidental) with a
    small superscript octave — e.g. a big "C" with a small "4", or "Bb" with
    a small "3".

    Self-centers horizontally on `center_x`; the top of the big letter aligns
    to `top_y`. Call set_note_name(name) to update it (pass None or "" to
    clear, e.g. on a rest)."""

    LETTER_SCALE = 3
    OCTAVE_SCALE = 2

    def __init__(self, color, center_x, top_y):
        super().__init__()
        self._center_x = center_x
        self._top_y = top_y

        self._main = label.Label(terminalio.FONT, text="", color=color, scale=self.LETTER_SCALE)
        self._main.anchor_point = (0.0, 0.0)
        self._octave = label.Label(terminalio.FONT, text="", color=color, scale=self.OCTAVE_SCALE)
        self._octave.anchor_point = (0.0, 0.0)

        self.append(self._main)
        self.append(self._octave)

    def set_note_name(self, name):
        if not name:
            self._main.text = ""
            self._octave.text = ""
            return

        letter, accidental, octave = display_parts(name)
        self._main.text = letter + _ACC_SYMBOL.get(accidental, "")
        self._octave.text = octave

        # bounding_box width is in unscaled glyph units, so multiply by scale.
        main_w = self._main.bounding_box[2] * self.LETTER_SCALE
        oct_w = self._octave.bounding_box[2] * self.OCTAVE_SCALE
        left = self._center_x - (main_w + oct_w) // 2

        self._main.anchored_position = (left, self._top_y)
        # Octave sits at the top-right of the letter so it reads as a superscript.
        self._octave.anchored_position = (left + main_w, self._top_y)