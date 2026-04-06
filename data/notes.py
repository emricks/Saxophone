class Accidental:
    SHARP = "sharp"
    FLAT = "flat"

class Note:
    def __init__(self, name, midi_number, fingerings, staff_y_coord, accidental=None):
        self.name = name
        self.midi_number = midi_number
        self.fingerings = set(fingerings)  # A set of integer bitmasks
        self.staff_y_coord = staff_y_coord
        self.accidental = accidental


class Notes:
    C_4 = Note(name="C_4", midi_number=51, fingerings={0b1111000000111}, staff_y_coord=143)
    D_4 = Note(name="D_4", midi_number=53, fingerings={0b1110000000111}, staff_y_coord=132)
    E_FLAT_4 = Note(name="E_FLAT_4", midi_number=54, fingerings={0b1110100000111}, staff_y_coord=121, accidental=Accidental.FLAT)
    E_4 = Note(name="E_4", midi_number=55, fingerings={0b1110000000011}, staff_y_coord=121)
    F_4 = Note(name="F_4", midi_number=56, fingerings={0b1110000000001}, staff_y_coord=110)
    F_SHARP_4 = Note(name="F_4", midi_number=57, fingerings={0b1110000000010,0b1110000000010001}, staff_y_coord=110, accidental=Accidental.SHARP)
    G_4 = Note(name="G_4", midi_number=58, fingerings={0b1110000000000}, staff_y_coord=99)
    A_4 = Note(name="A_4", midi_number=60, fingerings={0b0110000000000}, staff_y_coord=88)
    B_4 = Note(name="B_4", midi_number=62, fingerings={0b0010000000000}, staff_y_coord=77)
    C_5 = Note(name="C_5", midi_number=63, fingerings={0b0100000000000}, staff_y_coord=66)

    ALL = (C_4, D_4, E_FLAT_4, E_4, F_4, F_SHARP_4, G_4, A_4, B_4, C_5)
    # Build a reverse lookup dictionary for instant access: bitmask -> Note
    MASK_TO_NOTE = {}

    for note in ALL:
        for mask in note.fingerings:
            MASK_TO_NOTE[mask] = note


def note_from_mask(mask):
    note = Notes.MASK_TO_NOTE.get(mask, None)
    return note
