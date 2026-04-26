MAIN_MENU = {
    "title": "MAIN MENU", # Only the root needs an explicit title
    "type": "menu",
    "items": [
        {
            "text": "DRILLS",
            "type": "menu",
            "items": [
                {
                    "text": "Scales",
                    "type": "menu",
                    "items": [
                        {
                            "text": "Major Scales",
                            "type": "menu",
                            "items": [
                                {
                                    "text": "C Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "C Major",
                                        "key_signature": "C_MAJOR",
                                        "notes": ["C_4", "D_4", "E_4", "F_4", "G_4", "A_4", "B_4", "C_5"]
                                    }
                                },
                                {
                                    "text": "F Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "F Major",
                                        "key_signature": "F_MAJOR",
                                        "notes": ["F_4", "G_4", "A_4", "B_FLAT_4", "C_5", "D_5", "E_5", "F_5"]
                                    }
                                },
                                {
                                    "text": "Bb Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Bb Major",
                                        "key_signature": "B_FLAT_MAJOR",
                                        "notes": ["B_FLAT_4", "C_5", "D_5", "E_FLAT_5", "F_5", "G_5", "A_5", "B_FLAT_5"]
                                    }
                                },
                                {
                                    "text": "Eb Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Eb Major",
                                        "key_signature": "E_FLAT_MAJOR",
                                        "notes": ["E_FLAT_4", "F_4", "G_4", "A_FLAT_4", "B_FLAT_4", "C_5", "D_5", "E_FLAT_5"]
                                    }
                                },
                                {
                                    "text": "Ab Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Ab Major",
                                        "key_signature": "A_FLAT_MAJOR",
                                        "notes": ["A_FLAT_4", "B_FLAT_4", "C_5", "D_FLAT_5", "E_FLAT_5", "F_5", "G_5", "A_FLAT_5"]
                                    }
                                },
                                {
                                    "text": "Db Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Db Major",
                                        "key_signature": "D_FLAT_MAJOR",
                                        "notes": ["D_FLAT_4", "E_FLAT_4", "F_4", "G_FLAT_4", "A_FLAT_4", "B_FLAT_4", "C_5", "D_FLAT_5"]
                                    }
                                },
                                {
                                    "text": "Gb Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Gb Major",
                                        "key_signature": "G_FLAT_MAJOR",
                                        "notes": ["G_FLAT_4", "A_FLAT_4", "B_FLAT_4", "C_FLAT_5", "D_FLAT_5", "E_FLAT_5", "F_5", "G_FLAT_5"]
                                    }
                                },
                                {
                                    "text": "B Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "B Major",
                                        "key_signature": "B_MAJOR",
                                        "notes": ["B_4", "C_SHARP_5", "D_SHARP_5", "E_5", "F_SHARP_5", "G_SHARP_5", "A_SHARP_5", "B_5"]
                                    }
                                },
                                {
                                    "text": "E Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "E Major",
                                        "key_signature": "E_MAJOR",
                                        "notes": ["E_4", "F_SHARP_4", "G_SHARP_4", "A_4", "B_4", "C_SHARP_5", "D_SHARP_5", "E_5"]
                                    }
                                },
                                {
                                    "text": "A Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "A Major",
                                        "key_signature": "A_MAJOR",
                                        "notes": ["A_4", "B_4", "C_SHARP_5", "D_5", "E_5", "F_SHARP_5", "G_SHARP_5", "A_5"]
                                    }
                                },
                                {
                                    "text": "D Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "D Major",
                                        "key_signature": "D_MAJOR",
                                        "notes": ["D_4", "E_4", "F_SHARP_4", "G_4", "A_4", "B_4", "C_SHARP_5", "D_5"]
                                    }
                                },
                                {
                                    "text": "G Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "G Major",
                                        "key_signature": "G_MAJOR",
                                        "notes": ["G_4", "A_4", "B_4", "C_5", "D_5", "E_5", "F_SHARP_5", "G_5"]
                                    }
                                },
                                {"text": "< Back", "type": "back"}
                            ]
                        },
                    ]
                },
                {"text": "< Back", "type": "back"}
            ]
        },
        {
            "text": "SONGS",
            "type": "song"
        },
        {
            "text": "FREE PLAY",
            "type": "play"
        },
        {
            "text": "SETTINGS",
            "type": "menu",
            "items": [
                {
                    "text": "Color",
                    "type": "menu",
                    "items": [
                        {"text": "Hulk", "type": "color", "payload": {
                            "name": "Hulk",
                            "bg_color": 0x000000,
                            "fg_color": 0x00FE03,
                            "chart_color": 0x00FE03,
                            "fingering_color": 0xFF01FC,
                            "drill_note_color": 0xFF6000
                        }},
                        {"text": "Christmas", "type": "color", "payload": {
                            "name": "Christmas",
                            "bg_color": 0xFF2222,
                            "fg_color": 0x00DD00,
                            "chart_color": 0x00DD00,
                            "fingering_color": 0xFFFF80,
                            "drill_note_color": 0xCCCCCC
                        }},
                        {"text": "Default", "type": "color", "payload": {
                            "name": "Default",
                            "bg_color": 0x0000FF,
                            "fg_color": 0xFFFFFF,
                            "chart_color": 0xFFFFFF,
                            "fingering_color": 0xFF0000,
                            "drill_note_color": 0x00FF00
                        }},
                        {"text": "> Back", "type": "back"}
                    ]
                },
                {
                    "text": "Volume",
                    "type": "menu",
                    "items": [
                        {
                            "text": "Coming Soon"
                        },
                        {"text": "< Back", "type": "back"}
                    ]
                },
                {"text": "< Back", "type": "back"}
            ]
        }
    ]
}