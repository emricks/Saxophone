from hardware.buttons import Buttons

class Accidental:
    SHARP: str = "sharp"
    FLAT: str = "flat"
    NATURAL: str = "natural"

class Duration:
    WHOLE: str = "whole"
    HALF: str = "half"
    QUARTER: str = "quarter"
    EIGHTH: str = "eighth"

class Rest:
    def __init__(self, duration: str) -> None:
        self.duration = duration

class Note:
    def __init__(self, name: str, midi_number: int, fingerings: set, ledger_line: float, accidental: str | None = None) -> None:
        self.name = name
        self.midi_number = midi_number
        self.button_fingerings = fingerings
        self.ledger_line = ledger_line
        self.accidental = accidental

        self.fingerings: set[int] = set()
        for button_group in fingerings:
            mask = 0
            for button in button_group:
                mask |= (1 << button.fingering_bit)
            self.fingerings.add(mask)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Note):
            return NotImplemented
        return self.midi_number == other.midi_number

    def __hash__(self) -> int:
        return hash(self.midi_number)

class TimedNote:
    def __init__(self, note: Note, duration: str) -> None:
        self.note = note
        self.duration = duration

class Notes:
    B_FLAT_3 = Note(name="B_FLAT_3", midi_number=49, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_B_FLAT)
    }, ledger_line=-1.5, accidental=Accidental.FLAT)
    B_3 = Note(name="B_3", midi_number=50, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_B)
    }, ledger_line=-1.5)
    # Cb is enharmonic to B (one half-step below C). Drawn on the C line.
    C_FLAT_4 = Note(name="C_FLAT_4", midi_number=50, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_B)
    }, ledger_line=-1.0, accidental=Accidental.FLAT)

    C_4 = Note(name="C_4", midi_number=51, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C)
    }, ledger_line=-1.0)
    C_SHARP_4 = Note(name="C_SHARP_4", midi_number=52, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_C_SHARP)
    }, ledger_line=-1.0, accidental=Accidental.SHARP)
    # Db is enharmonic to C#. Drawn in the D space.
    D_FLAT_4 = Note(name="D_FLAT_4", midi_number=52, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C,
         Buttons.L_LOW_C_SHARP)
    }, ledger_line=-0.5, accidental=Accidental.FLAT)
    D_4 = Note(name="D_4", midi_number=53, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3)
    }, ledger_line=-0.5)
    E_FLAT_4 = Note(name="E_FLAT_4", midi_number=54, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_E_FLAT)
    }, ledger_line=0.0, accidental=Accidental.FLAT)
    # D# is enharmonic to Eb (same fingering, same staff position) but is
    # named distinctly so the key-signature renderer can identify it as a "D".
    D_SHARP_4 = Note(name="D_SHARP_4", midi_number=54, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_E_FLAT)
    }, ledger_line=0.0, accidental=Accidental.SHARP)
    E_4 = Note(name="E_4", midi_number=55, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2)
    }, ledger_line=0.0)
    # Fb is enharmonic to E (one half-step below F). Drawn on the F line.
    F_FLAT_4 = Note(name="F_FLAT_4", midi_number=55, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2)
    }, ledger_line=0.5, accidental=Accidental.FLAT)
    F_4 = Note(name="F_4", midi_number=56, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1)
    }, ledger_line=0.5)
    # E# is enharmonic to F.
    E_SHARP_4 = Note(name="E_SHARP_4", midi_number=56, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1)
    }, ledger_line=0.5, accidental=Accidental.SHARP)
    F_SHARP_4 = Note(name="F_SHARP_4", midi_number=57, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_2),
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_F_SHARP)
    }, ledger_line=0.5, accidental=Accidental.SHARP)
    # Gb is enharmonic to F#. Drawn on the G line.
    G_FLAT_4 = Note(name="G_FLAT_4", midi_number=57, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_2),
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_F_SHARP)
    }, ledger_line=1.0, accidental=Accidental.FLAT)
    G_4 = Note(name="G_4", midi_number=58, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3)
    }, ledger_line=1.0)
    A_FLAT_4 = Note(name="A_FLAT_4", midi_number=59, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.L_G_SHARP)
    }, ledger_line=1.5, accidental=Accidental.FLAT)
    # G# is enharmonic to Ab.
    G_SHARP_4 = Note(name="G_SHARP_4", midi_number=59, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.L_G_SHARP)
    }, ledger_line=1.0, accidental=Accidental.SHARP)
    A_4 = Note(name="A_4", midi_number=60, fingerings={
        (Buttons.L_1, Buttons.L_2)
    }, ledger_line=1.5)
    B_FLAT_4 = Note(name="B_FLAT_4", midi_number=61, fingerings={
        (Buttons.L_1, Buttons.R_1),
        (Buttons.L_1, Buttons.R_2),
        (Buttons.L_1, Buttons.L_2, Buttons.R_B_FLAT),
        (Buttons.L_1, Buttons.L_B_FLAT),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_B_FLAT),
    }, ledger_line=2.0, accidental=Accidental.FLAT)
    # A# is enharmonic to Bb.
    A_SHARP_4 = Note(name="A_SHARP_4", midi_number=61, fingerings={
        (Buttons.L_1, Buttons.R_1),
        (Buttons.L_1, Buttons.R_2),
        (Buttons.L_1, Buttons.L_2, Buttons.R_B_FLAT),
        (Buttons.L_1, Buttons.L_B_FLAT),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_B_FLAT),
    }, ledger_line=1.5, accidental=Accidental.SHARP)
    B_4 = Note(name="B_4", midi_number=62, fingerings={
        (Buttons.L_1,),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_B),
    }, ledger_line=2.0)

    C_5 = Note(name="C_5", midi_number=63, fingerings={
        (Buttons.L_2,),
        (Buttons.L_1, Buttons.R_C),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C)
    }, ledger_line=2.5)
    # B# is enharmonic to C.
    B_SHARP_4 = Note(name="B_SHARP_4", midi_number=63, fingerings={
        (Buttons.L_2,),
        (Buttons.L_1, Buttons.R_C),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C)
    }, ledger_line=2.0, accidental=Accidental.SHARP)
    C_SHARP_5 = Note(name="C_SHARP_5", midi_number=64, fingerings={
        tuple(),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_C_SHARP),
    }, ledger_line=2.5, accidental=Accidental.SHARP)
    D_5 = Note(name="D_5", midi_number=65, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3)
    }, ledger_line=3.0)
    E_FLAT_5 = Note(name="E_FLAT_5", midi_number=66, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_E_FLAT)
    }, ledger_line=3.5, accidental=Accidental.FLAT)
    E_5 = Note(name="E_5", midi_number=67, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2)
    }, ledger_line=3.5)
    F_5 = Note(name="F_5", midi_number=68, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1)
    }, ledger_line=4.0)
    F_SHARP_5 = Note(name="F_SHARP_5", midi_number=69, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_2),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_F_SHARP)
    }, ledger_line=4.0, accidental=Accidental.SHARP)
    G_5 = Note(name="G_5", midi_number=70, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3)
    }, ledger_line=4.5)
    A_FLAT_5 = Note(name="A_FLAT_5", midi_number=71, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.L_G_SHARP)
    }, ledger_line=5.0, accidental=Accidental.FLAT)
    A_5 = Note(name="A_5", midi_number=72, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2)
    }, ledger_line=5.0)
    B_FLAT_5 = Note(name="B_FLAT_5", midi_number=73, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.R_1),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.R_2),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_B_FLAT),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.R_B_FLAT),

    }, ledger_line=5.5, accidental=Accidental.FLAT)
    B_5 = Note(name="B_5", midi_number=74, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1)
    }, ledger_line=5.5)

    C_6 = Note(name="C_6", midi_number=75, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_2),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.R_C)
    }, ledger_line=6.0)
    C_SHARP_6 = Note(name="C_SHARP_6", midi_number=76, fingerings={
        (Buttons.L_OCTAVE,)
    }, ledger_line=6.0, accidental=Accidental.SHARP)
    D_6 = Note(name="D_6", midi_number=77, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_D)
    }, ledger_line=6.5)
    E_FLAT_6 = Note(name="E_FLAT_6", midi_number=78, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_D, Buttons.L_E_FLAT)
    }, ledger_line=7.0, accidental=Accidental.FLAT)
    E_6 = Note(name="E_6", midi_number=79, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_D, Buttons.L_E_FLAT, Buttons.R_E),
        (Buttons.L_OCTAVE, Buttons.L_2, Buttons.L_3, Buttons.L_FRONT_F)
    }, ledger_line=7.0)
    F_6 = Note(name="F_6", midi_number=80, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_2, Buttons.L_FRONT_F),
        (Buttons.L_OCTAVE, Buttons.L_D, Buttons.L_E_FLAT, Buttons.L_F, Buttons.R_E),
    }, ledger_line=7.5)
    F_SHARP_6 = Note(name="F_SHARP_6", midi_number=81, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_2, Buttons.L_FRONT_F, Buttons.R_HIGH_F_SHARP)
    }, ledger_line=7.5, accidental=Accidental.SHARP)

    ALL = (B_FLAT_3, B_3,
           C_4, C_SHARP_4, D_4, E_FLAT_4, E_4, F_4, F_SHARP_4, G_4, A_FLAT_4, A_4, B_FLAT_4, B_4,
           C_5, C_SHARP_5, D_5, E_FLAT_5, E_5, F_5, F_SHARP_5, G_5, A_FLAT_5, A_5, B_FLAT_5, B_5,
           C_6, C_SHARP_6, D_6, E_FLAT_6, E_6, F_6, F_SHARP_6)
    C_LINE = {B_FLAT_3, B_3, C_4, C_SHARP_4}
    A_LINE = {A_FLAT_5, A_5, B_FLAT_5, B_5, C_6, C_SHARP_6, D_6, E_FLAT_6, E_6, F_6, F_SHARP_6}
    HIGH_C_LINE = {C_6, C_SHARP_6, D_6, E_FLAT_6, E_6, F_6, F_SHARP_6}
    E_LINE = {E_FLAT_6, E_6, F_6, F_SHARP_6}
    # Build a reverse lookup dictionary for instant access: bitmask -> Note
    MASK_TO_NOTE = {}

    for note in ALL:
        for mask in note.fingerings:
            MASK_TO_NOTE[mask] = note

    @staticmethod
    def get_note_by_name(name) -> Note | None:
        """Returns the Note instance corresponding to the given name string."""
        return getattr(Notes, name, None)


def note_from_mask(mask):
    note = Notes.MASK_TO_NOTE.get(mask, None)
    return note
