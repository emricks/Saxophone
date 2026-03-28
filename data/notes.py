class Note:
    def __init__(self, name, midi_number, fingerings, staff_y_coord):
        self.name = name
        self.midi_number = midi_number
        self.fingerings = set(fingerings)  # A set of integer bitmasks
        self.staff_y_coord = staff_y_coord


class Notes:
    C_2 = Note(name="C_2", midi_number=36, fingerings={0b1000000111}, staff_y_coord=140)
    D_2 = Note(name="D_2", midi_number=38, fingerings={0b0000000111}, staff_y_coord=130)
    E_FLAT_2 = Note(name="E_FLAT_2", midi_number=39, fingerings={0b0100000111}, staff_y_coord=120)
    E_2 = Note(name="E_2", midi_number=40, fingerings={0b0000000011}, staff_y_coord=110)
    F_2 = Note(name="F_2", midi_number=41, fingerings={0b0000000001}, staff_y_coord=100)
    F_SHARP_2 = Note(name="F_2", midi_number=42, fingerings={0b0000000010,0b0000010001}, staff_y_coord=100)


    ALL = (C_2, D_2, E_FLAT_2, E_2, F_2, F_SHARP_2)
    # Build a reverse lookup dictionary for instant access: bitmask -> Note
    MASK_TO_NOTE = {}

    for note in ALL:
        for mask in note.fingerings:
            MASK_TO_NOTE[mask] = note


def note_from_mask(mask):
    note = Notes.MASK_TO_NOTE.get(mask, None)
    return note
