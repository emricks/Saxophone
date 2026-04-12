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
                            "type": "menu",
                            "items": [
                                {
                                    "text": "In Order",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "C Major",
                                        "notes": ["C_4", "D_4", "E_4", "F_4", "G_4", "A_4", "B_4", "C_5"]
                                    }
                                },
                                {
                                    "text": "Random",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "C Major (Random)",
                                        "notes": ["C_4", "D_4", "E_4", "F_4", "G_4", "A_4", "B_4", "C_5"]
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
                            "fingering_color": 0xFF01FC
                        }},
                        {"text": "Christmas", "type": "color", "payload": {
                            "name": "Christmas",
                            "bg_color": 0xFF4444,
                            "fg_color": 0x00BB00,
                            "chart_color": 0x00BB00,
                            "fingering_color": 0xFFFF00
                        }},
                        {"text": "Default", "type": "color", "payload": {
                            "name": "Default",
                            "bg_color": 0x0000FF,
                            "fg_color": 0xFFFFFF,
                            "chart_color": 0xFFFFFF,
                            "fingering_color": 0xFF0000
                        }},
                        {"text": "> Back", "type": "back"}
                    ]
                },
                {"text": "< Back", "type": "back"}
            ]
        }
    ]
}