from composer.notes import Note, Notes

class KeySignature:
    """
    Represents a musical key signature.
    Determines which notes are naturally sharp or flat, and provides
    the necessary logic to draw the correct accidentals on a staff.
    """

    def __init__(self, key_name: str, notes: list[Note] | None = None) -> None:
        self.key_name = key_name
        self.notes: list[Note] = notes or []
        self.accidentals: list[Note] = self._get_accidentals()

    def _get_accidentals(self) -> list[Note]:
        """Returns the subset of key notes that carry an accidental, in standard staff order."""
        accidentals = []

        for note in self.notes:
            if note.accidental is not None:
                accidentals.append(note)

        # Sort them by standard Key Signature order.
        # Sharps order: F, C, G, D, A, E, B
        # Flats order: B, E, A, D, G, C, F
        sharp_order = {"F": 0, "C": 1, "G": 2, "D": 3, "A": 4, "E": 5, "B": 6}
        flat_order = {"B": 0, "E": 1, "A": 2, "D": 3, "G": 4, "C": 5, "F": 6}

        def sort_key(note):
            base_name = note.name.split("_")[0]
            if note.accidental == "sharp":
                return sharp_order.get(base_name, 99)
            elif note.accidental == "flat":
                return flat_order.get(base_name, 99)
            return 99

        accidentals.sort(key=sort_key)
        return accidentals

class KeySignatures:
    C_MAJOR = KeySignature("Cmaj", [])
    G_MAJOR = KeySignature("Gmaj", [Notes.F_SHARP_4])
    D_MAJOR = KeySignature("Dmaj", [Notes.F_SHARP_4, Notes.C_SHARP_4])
    A_MAJOR = KeySignature("Amaj", [Notes.F_SHARP_4, Notes.C_SHARP_4, Notes.G_SHARP_4])
    E_MAJOR = KeySignature("Emaj", [Notes.F_SHARP_4, Notes.C_SHARP_4, Notes.G_SHARP_4, Notes.D_SHARP_4])

    B_MAJOR = KeySignature("Bmaj", [Notes.F_SHARP_4, Notes.C_SHARP_4, Notes.G_SHARP_4, Notes.D_SHARP_4, Notes.A_SHARP_4])
    C_FLAT_MAJOR = KeySignature("Cbmaj",[Notes.B_FLAT_4, Notes.E_FLAT_4, Notes.A_FLAT_4, Notes.D_FLAT_4, Notes.G_FLAT_4,Notes.C_FLAT_4, Notes.F_FLAT_4])

    F_SHARP_MAJOR = KeySignature("F#maj", [Notes.F_SHARP_4, Notes.C_SHARP_4, Notes.G_SHARP_4, Notes.D_SHARP_4, Notes.A_SHARP_4, Notes.E_SHARP_4])
    G_FLAT_MAJOR = KeySignature("Gbmaj",[Notes.B_FLAT_4, Notes.E_FLAT_4, Notes.A_FLAT_4, Notes.D_FLAT_4, Notes.G_FLAT_4, Notes.C_FLAT_4])

    C_SHARP_MAJOR = KeySignature("C#maj", [Notes.F_SHARP_4, Notes.C_SHARP_4, Notes.G_SHARP_4, Notes.D_SHARP_4, Notes.A_SHARP_4, Notes.E_SHARP_4, Notes.B_SHARP_4])
    D_FLAT_MAJOR = KeySignature("Dbmaj", [Notes.B_FLAT_4, Notes.E_FLAT_4, Notes.A_FLAT_4, Notes.D_FLAT_4, Notes.G_FLAT_4])

    A_FLAT_MAJOR = KeySignature("Abmaj", [Notes.B_FLAT_4, Notes.E_FLAT_4, Notes.A_FLAT_4, Notes.D_FLAT_4])
    E_FLAT_MAJOR = KeySignature("Ebmaj", [Notes.B_FLAT_4, Notes.E_FLAT_4, Notes.A_FLAT_4])
    B_FLAT_MAJOR = KeySignature("Bbmaj", [Notes.B_FLAT_4, Notes.E_FLAT_4])
    F_MAJOR = KeySignature("Fmaj", [Notes.B_FLAT_4])

    C_MINOR = KeySignature("Cmin", [Notes.B_FLAT_4, Notes.E_FLAT_4, Notes.A_FLAT_4])

