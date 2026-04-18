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
                            "text": "C Major Scale",
                            "type": "scale_drill",
                            "payload": {
                                "name": "C Major",
                                "notes": ["C_4", "D_4", "E_4", "F_4", "G_4", "A_4", "B_4", "C_5"]
                            }
                        },
                        {
                            "text": "D Major Scale",
                            "type": "scale_drill",
                            "payload": {
                                "name": "D Major",
                                "notes": ["D_4", "E_4", "F_SHARP_4", "G_4", "A_4", "B_4", "C_SHARP_5", "D_5"]
                            }
                        },
                        {
                            "text": "E Major Scale",
                            "type": "scale_drill",
                            "payload": {
                                "name": "E Major",
                                "notes": ["E_4", "F_SHARP_4", "A_FLAT_4", "A_4", "B_4", "C_SHARP_5", "E_FLAT_5", "E_5"]
                            }
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
                            "test_note_color": 0xFF6000
                        }},
                        {"text": "Christmas", "type": "color", "payload": {
                            "name": "Christmas",
                            "bg_color": 0xFF2222,
                            "fg_color": 0x00DD00,
                            "chart_color": 0x00DD00,
                            "fingering_color": 0xFFFF80,
                            "test_note_color": 0xCCCCCC
                        }},
                        {"text": "Default", "type": "color", "payload": {
                            "name": "Default",
                            "bg_color": 0x0000FF,
                            "fg_color": 0xFFFFFF,
                            "chart_color": 0xFFFFFF,
                            "fingering_color": 0xFF0000,
                            "test_note_color": 0x00FF00
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