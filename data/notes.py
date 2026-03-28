class Note:
    def __init__(self, name, midi_number, fingerings, staff_y_coord):
        self.name = name
        self.midi_number = midi_number
        self.fingerings = set(fingerings)  # A set of integer bitmasks
        self.staff_y_coord = staff_y_coord


class Notes:
    E2 = Note(name="E2", midi_number=40, fingerings={0b0000000001}, staff_y_coord=60)
    F2 = Note(name="F2", midi_number=41, fingerings={0b0000000010}, staff_y_coord=70)
    G2 = Note(name="G2", midi_number=43, fingerings={0b0000000100}, staff_y_coord=80)
    A2 = Note(name="A2", midi_number=45, fingerings={0b0000001000}, staff_y_coord=90)
    B2 = Note(name="B2", midi_number=47, fingerings={0b0000010000}, staff_y_coord=100)
    C3 = Note(name="C3", midi_number=48, fingerings={0b0000100000}, staff_y_coord=110)
    D3 = Note(name="D3", midi_number=50, fingerings={0b0001000000}, staff_y_coord=120)
    E3 = Note(name="E3", midi_number=52, fingerings={0b0010000000}, staff_y_coord=130)
    F3 = Note(name="F3", midi_number=53, fingerings={0b0100000000}, staff_y_coord=140)
    G3 = Note(name="G3", midi_number=55, fingerings={0b1000000000}, staff_y_coord=140)

    ALL = (E2, F2, G2, A2, B2, C3, D3, E3, F3, G3)

    # Build a reverse lookup dictionary for instant access: bitmask -> Note
    MASK_TO_NOTE = {}

    for note in ALL:
        for mask in note.fingerings:
            MASK_TO_NOTE[mask] = note


def note_from_mask(mask):
    note = Notes.MASK_TO_NOTE.get(mask, None)
    return note
