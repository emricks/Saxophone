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
                            "text": "C Major",
                            "type": "menu",
                            "items": [
                                {
                                    "text": "C Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "C Major",
                                        "key_signature": "C_MAJOR",
                                        "notes": ["C_4", "D_4", "E_4", "F_4", "G_4", "A_4", "B_4", "C_5", "B_4", "A_4", "G_4", "F_4", "E_4", "D_4", "C_4"]
                                    }
                                },
                                {
                                    "text": "C Major Scale (Ext)",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "C Major",
                                        "key_signature": "C_MAJOR",
                                        "notes": ["C_4", "D_4", "E_4", "F_4", "G_4", "A_4", "B_4", "C_5", "D_5", "E_5", "F_5", "G_5", "A_5", "B_5", "C_6", "D_6", "E_6", "F_6"]
                                    }
                                },
                                {
                                    "text": "C Major Thirds",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "C Major Thirds",
                                        "key_signature": "C_MAJOR",
                                        "notes": ["C_4", "E_4", "D_4", "F_4", "E_4", "G_4", "F_4", "A_4", "G_4", "B_4", "A_4", "C_5", "B_4", "D_5", "C_5", "A_4", "B_4", "G_4", "A_4", "F_4", "G_4", "E_4", "F_4", "D_4", "E_4", "C_4"]
                                    }
                                },
                                {
                                    "text": "C Blues Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "C Blues",
                                        "key_signature": "C_MAJOR",
                                        "notes": ["C_4", "E_FLAT_4", "F_4", "F_SHARP_4", "G_4", "B_FLAT_4", "C_5", "B_FLAT_4", "G_4", "F_SHARP_4", "F_4", "E_FLAT_4", "C_4"]
                                    }
                                },
                                {"text": "< Back", "type": "back"}
                            ]
                        },
                        {
                            "text": "D Major",
                            "type": "menu",
                            "items": [
                                {
                                    "text": "D Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "D Major",
                                        "key_signature": "D_MAJOR",
                                        "notes": ["D_4", "E_4", "F_SHARP_4", "G_4", "A_4", "B_4", "C_SHARP_5", "D_5", "C_SHARP_5", "B_4", "A_4", "G_4", "F_SHARP_4", "E_4", "D_4"]
                                    }
                                },
                                {"text": "< Back", "type": "back"}
                            ]
                        },
                        {
                            "text": "E Major",
                            "type": "menu",
                            "items": [
                                {
                                    "text": "E Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "E Major",
                                        "key_signature": "E_MAJOR",
                                        "notes": ["E_4", "F_SHARP_4", "A_FLAT_4", "A_4", "B_4", "C_SHARP_5", "E_FLAT_5", "E_5", "E_FLAT_5", "C_SHARP_5", "B_4", "A_4", "A_FLAT_4", "F_SHARP_4", "E_4"]
                                    }
                                },
                                {"text": "< Back", "type": "back"}
                            ]
                        },
                        {"text": "< Back", "type": "back"}
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