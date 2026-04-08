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
                                        "name": "C Major",
                                        "notes": ["C_4", "D_4", "E_4", "F_4", "G_4", "A_4", "B_4", "C_5"]
                                    }
                                }
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
            "type": "menu",
            "items": [
                {"text": "COMING SOON", "type": "info"},
                {"text": "< Back", "type": "back"}
            ]
        },
        {
            "text": "FREE PLAY",
            "type": "play"
        }
    ]
}