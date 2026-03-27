MAIN_MENU = {
    "title": "MAIN MENU", # Only the root needs an explicit title
    "type": "menu",
    "items": [
        {
            "text": "DRILLS",
            "type": "menu",
            "items": [
                {
                    "text": "SIGHT READING",
                    "type": "menu",
                    "items": [
                        {
                            "text": "C Major Scale",
                            "type": "drill",
                            "payload": {
                                "name": "C Major",
                                "notes": ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
                            }
                        },
                        {
                            "text": "G Pentatonic",
                            "type": "drill",
                            "payload": {
                                "name": "G Pentatonic",
                                "notes": ["G4", "A4", "B4", "D5", "E5"]
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
            "type": "menu",
            "items": [
                {"text": "COMING SOON", "type": "info"},
                {"text": "< Back", "type": "back"}
            ]
        },
    ]
}