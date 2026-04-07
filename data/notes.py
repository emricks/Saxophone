from hardware.buttons import Buttons

class Accidental:
    SHARP = "sharp"
    FLAT = "flat"

class Note:
    def __init__(self, name, midi_number, fingerings, staff_y_coord, accidental=None):
        self.name = name
        self.midi_number = midi_number
        self.button_fingerings = fingerings
        self.staff_y_coord = staff_y_coord
        self.accidental = accidental

        self.fingerings = set()
        for button_group in fingerings:
            mask = 0
            for button in button_group:
                mask |= (1 << button.fingering_bit)
            self.fingerings.add(mask)


class Notes:
    B_FLAT_3 = Note(name="B_FLAT_3", midi_number=49, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_B_FLAT)
    }, staff_y_coord=165, accidental=Accidental.FLAT)
    B_3 = Note(name="B_3", midi_number=50, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_B)
    }, staff_y_coord=165)

    C_4 = Note(name="C_4", midi_number=51, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C)
    }, staff_y_coord=154)
    C_SHARP_4 = Note(name="C_SHARP_4", midi_number=52, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_C_SHARP)
    }, staff_y_coord=154, accidental=Accidental.SHARP)
    D_4 = Note(name="D_4", midi_number=53, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3)
    }, staff_y_coord=143)
    E_FLAT_4 = Note(name="E_FLAT_4", midi_number=54, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_E_FLAT)
    }, staff_y_coord=132, accidental=Accidental.FLAT)
    E_4 = Note(name="E_4", midi_number=55, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2)
    }, staff_y_coord=132)
    F_4 = Note(name="F_4", midi_number=56, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1)
    }, staff_y_coord=121)
    F_SHARP_4 = Note(name="F_4", midi_number=57, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_2),
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_F_SHARP)
    }, staff_y_coord=121, accidental=Accidental.SHARP)
    G_4 = Note(name="G_4", midi_number=58, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3)
    }, staff_y_coord=110)
    A_FLAT_4 = Note(name="A_FLAT_4", midi_number=59, fingerings={
        (Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.L_G_SHARP)
    }, staff_y_coord=99, accidental=Accidental.FLAT)
    A_4 = Note(name="A_4", midi_number=60, fingerings={
        (Buttons.L_1, Buttons.L_2)
    }, staff_y_coord=99)
    B_FLAT_4 = Note(name="B_FLAT_4", midi_number=61, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_B_FLAT),
        (Buttons.L_1, Buttons.L_2, Buttons.R_B_FLAT),
        (Buttons.L_1, Buttons.L_B_FLAT),
        (Buttons.L_1, Buttons.R_1),
        (Buttons.L_1, Buttons.R_2),
    }, staff_y_coord=88, accidental=Accidental.FLAT)
    B_4 = Note(name="B_4", midi_number=62, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_B),
        (Buttons.L_1,)
    }, staff_y_coord=88)

    C_5 = Note(name="C_5", midi_number=63, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C),
        (Buttons.L_2,),
        (Buttons.L_1, Buttons.R_C)
    }, staff_y_coord=77)
    C_SHARP_5 = Note(name="C_SHARP_5", midi_number=64, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_C, Buttons.L_LOW_C_SHARP),
        tuple()
    }, staff_y_coord=77, accidental=Accidental.SHARP)
    D_5 = Note(name="D_5", midi_number=65, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3)
    }, staff_y_coord=66)
    E_FLAT_5 = Note(name="E_FLAT_5", midi_number=66, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2, Buttons.R_3, Buttons.R_LOW_E_FLAT)
    }, staff_y_coord=55, accidental=Accidental.FLAT)
    E_5 = Note(name="E_5", midi_number=67, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_2)
    }, staff_y_coord=55)
    F_5 = Note(name="F_5", midi_number=68, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1)
    }, staff_y_coord=44)
    F_SHARP_5 = Note(name="F_SHARP_5", midi_number=69, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_2),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.R_1, Buttons.R_F_SHARP)
    }, staff_y_coord=44, accidental=Accidental.SHARP)
    G_5 = Note(name="G_5", midi_number=70, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3)
    }, staff_y_coord=33)
    A_FLAT_5 = Note(name="A_FLAT_5", midi_number=71, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.L_3, Buttons.L_G_SHARP)
    }, staff_y_coord=22, accidental=Accidental.FLAT)
    A_5 = Note(name="A_5", midi_number=72, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2)
    }, staff_y_coord=22)
    B_FLAT_5 = Note(name="B_FLAT_5", midi_number=73, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_2, Buttons.R_B_FLAT),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.L_B_FLAT),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.R_1),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.R_2)
    }, staff_y_coord=11, accidental=Accidental.FLAT)
    B_5 = Note(name="B_5", midi_number=74, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_1)
    }, staff_y_coord=11)

    C_6 = Note(name="C_6", midi_number=75, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_2),
        (Buttons.L_OCTAVE, Buttons.L_1, Buttons.R_C)
    }, staff_y_coord=0)
    C_SHARP_6 = Note(name="C_SHARP_6", midi_number=76, fingerings={
        (Buttons.L_OCTAVE,)
    }, staff_y_coord=0, accidental=Accidental.SHARP)
    D_6 = Note(name="D_6", midi_number=77, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_D)
    }, staff_y_coord=-11)
    E_FLAT_6 = Note(name="E_FLAT_6", midi_number=78, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_D, Buttons.L_E_FLAT)
    }, staff_y_coord=-22, accidental=Accidental.FLAT)
    E_6 = Note(name="E_6", midi_number=79, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_D, Buttons.L_E_FLAT, Buttons.R_E),
        (Buttons.L_OCTAVE, Buttons.L_2, Buttons.L_3, Buttons.L_FRONT_F)
    }, staff_y_coord=-22)
    F_6 = Note(name="F_6", midi_number=80, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_D, Buttons.L_E_FLAT, Buttons.L_F, Buttons.R_E),
        (Buttons.L_OCTAVE, Buttons.L_2, Buttons.L_FRONT_F)
    }, staff_y_coord=-33)
    F_SHARP_6 = Note(name="F_SHARP_6", midi_number=81, fingerings={
        (Buttons.L_OCTAVE, Buttons.L_2, Buttons.L_FRONT_F, Buttons.R_HIGH_F_SHARP)
    }, staff_y_coord=-33, accidental=Accidental.SHARP)

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


def note_from_mask(mask):
    note = Notes.MASK_TO_NOTE.get(mask, None)
    return note
