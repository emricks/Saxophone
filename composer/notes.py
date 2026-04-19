class Accidental:
    SHARP = "sharp"
    FLAT = "flat"

class Note:
    def __init__(self, name, midi_number, fingerings, ledger_line, accidental=None):
        self.name = name
        self.midi_number = midi_number
        self.button_fingerings = fingerings
        self.ledger_line = ledger_line
        self.accidental = accidental

        self.fingerings = set()
        for button_group in fingerings:
            mask = 0
            for button in button_group:
                mask |= (1 << button.fingering_bit)
            self.fingerings.add(mask)