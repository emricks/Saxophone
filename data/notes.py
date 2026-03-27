class Note:
    def __init__(self, name, midi_number, fingerings, staff_y_coord):
        self.name = name
        self.midi_number = midi_number
        self.fingerings = set(fingerings)  # A set of integer bitmasks
        self.staff_y_coord = staff_y_coord


class Notes:
    G = Note(name="G", midi_number=67, fingerings={0b0001}, staff_y_coord=120)
    A = Note(name="A", midi_number=69, fingerings={0b0010}, staff_y_coord=110)
    B = Note(name="B", midi_number=71, fingerings={0b0011}, staff_y_coord=100)

    ALL = (G, A, B)

    # Build a reverse lookup dictionary for instant access: bitmask -> Note
    MASK_TO_NOTE = {}

    for note in ALL:
        for mask in note.fingerings:
            MASK_TO_NOTE[mask] = note


def note_from_mask(mask):
    return Notes.MASK_TO_NOTE.get(mask, None)
