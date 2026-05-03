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
                                        "notes": ["C_4", "D_4", "E_4", "F_4", "G_4", "A_4", "B_4", "C_5"],
                                        "mode": "revrand"
                                    }
                                },
                                {
                                    "text": "F Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "F Major",
                                        "key_signature": "F_MAJOR",
                                        "notes": ["F_4", "G_4", "A_4", "B_FLAT_4", "C_5", "D_5", "E_5", "F_5"],
                                        "mode": "revrand"
                                    }
                                },
                                {
                                    "text": "Bb Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Bb Major",
                                        "key_signature": "B_FLAT_MAJOR",
                                        "notes": ["B_FLAT_4", "C_5", "D_5", "E_FLAT_5", "F_5", "G_5", "A_5", "B_FLAT_5"],
                                        "mode": "revrand"
                                    }
                                },
                                {
                                    "text": "Eb Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Eb Major",
                                        "key_signature": "E_FLAT_MAJOR",
                                        "notes": ["E_FLAT_4", "F_4", "G_4", "A_FLAT_4", "B_FLAT_4", "C_5", "D_5", "E_FLAT_5"],
                                        "mode": "revrand"
                                    }
                                },
                                {
                                    "text": "Ab Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Ab Major",
                                        "key_signature": "A_FLAT_MAJOR",
                                        "notes": ["A_FLAT_4", "B_FLAT_4", "C_5", "D_FLAT_5", "E_FLAT_5", "F_5", "G_5", "A_FLAT_5"],
                                        "mode": "revrand"
                                    }
                                },
                                {
                                    "text": "Db Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Db Major",
                                        "key_signature": "D_FLAT_MAJOR",
                                        "notes": ["D_FLAT_4", "E_FLAT_4", "F_4", "G_FLAT_4", "A_FLAT_4", "B_FLAT_4", "C_5", "D_FLAT_5"],
                                        "mode": "revrand"
                                    }
                                },
                                {
                                    "text": "Gb Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Gb Major",
                                        "key_signature": "G_FLAT_MAJOR",
                                        "notes": ["G_FLAT_4", "A_FLAT_4", "B_FLAT_4", "C_FLAT_5", "D_FLAT_5", "E_FLAT_5", "F_5", "G_FLAT_5"],
                                        "mode": "revrand"
                                    }
                                },
                                {
                                    "text": "B Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "B Major",
                                        "key_signature": "B_MAJOR",
                                        "notes": ["B_4", "C_SHARP_5", "D_SHARP_5", "E_5", "F_SHARP_5", "G_SHARP_5", "A_SHARP_5", "B_5"],
                                        "mode": "revrand"
                                    }
                                },
                                {
                                    "text": "E Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "E Major",
                                        "key_signature": "E_MAJOR",
                                        "notes": ["E_4", "F_SHARP_4", "G_SHARP_4", "A_4", "B_4", "C_SHARP_5", "D_SHARP_5", "E_5"],
                                        "mode": "revrand"
                                    }
                                },
                                {
                                    "text": "A Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "A Major",
                                        "key_signature": "A_MAJOR",
                                        "notes": ["A_4", "B_4", "C_SHARP_5", "D_5", "E_5", "F_SHARP_5", "G_SHARP_5", "A_5"],
                                        "mode": "revrand"
                                    }
                                },
                                {
                                    "text": "D Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "D Major",
                                        "key_signature": "D_MAJOR",
                                        "notes": ["D_4", "E_4", "F_SHARP_4", "G_4", "A_4", "B_4", "C_SHARP_5", "D_5"],
                                        "mode": "revrand"
                                    }
                                },
                                {
                                    "text": "G Major Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "G Major",
                                        "key_signature": "G_MAJOR",
                                        "notes": ["G_4", "A_4", "B_4", "C_5", "D_5", "E_5", "F_SHARP_5", "G_5"],
                                        "mode": "revrand"
                                    }
                                },
                                {"text": "< Back", "type": "back"}
                            ]
                        },
                        {
                            "text": "Blues Scales",
                            "type": "menu",
                            "items": [
                                {
                                    "text": "C Blues Scale (basic)",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "C Blues",
                                        "key_signature": "C_MAJOR",
                                        "notes": ["C_4", "E_FLAT_4", "F_4", "F_SHARP_4", "G_4", "B_FLAT_4", "C_5", "B_FLAT_4", "G_4", "F_SHARP_4", "F_4", "E_FLAT_4", "C_4"]
                                    }
                                },
                                {
                                    "text": "C Blues Scale",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "C Blues",
                                        "key_signature": "C_MAJOR",
                                        "notes": ["C_4", "E_FLAT_4", "F_4", "E_FLAT_4", "F_4", "F_SHARP_4","F_4", "F_SHARP_4",
                                                  "G_4", "F_SHARP_4", "G_4", "B_FLAT_4", "G_4", "B_FLAT_4", "C_5", "B_FLAT_4",
                                                  "G_4", "B_FLAT_4", "G_4", "F_SHARP_4", "G_4", "F_SHARP_4", "F_4", "F_SHARP_4",
                                                  "F_4", "E_FLAT_4", "C_4"]
                                    }
                                },
                                {"text": "< Back", "type": "back"}
                            ]
                        },
                        {
                            "text": "Thirds Scales",
                            "type": "menu",
                            "items": [
                                {
                                    "text": "C Major Thirds",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "C Major Thirds",
                                        "key_signature": "C_MAJOR",
                                        "notes": ["C_4", "E_4", "D_4", "F_4", "E_4", "G_4", "F_4", "A_4", "G_4", "B_4", "A_4",
                                                  "C_5", "B_4", "D_5", "C_5", "REST_QUARTER", "E_5", "C_5", "D_5", "B_4", "C_5", "A_4", "B_4",
                                                  "G_4", "A_4", "F_4", "G_4", "E_4", "F_4", "D_4", "C_4"],
                                        "mode": "none"
                                    }
                                },
                                {
                                    "text": "F Major Thirds",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "F Major Thirds",
                                        "key_signature": "F_MAJOR",
                                        "notes": ["F_4", "A_4", "G_4", "B_FLAT_4", "A_4", "C_5", "B_FLAT_4", "D_5", "C_5",
                                                  "E_5", "D_5", "F_5", "E_5", "G_5", "F_5", "REST_QUARTER", "A_5", "F_5", "G_5", "E_5",
                                                  "F_5", "D_5", "E_5", "C_5", "D_5", "B_FLAT_4", "C_5", "A_4", "B_FLAT_4",
                                                  "G_4", "F_4"],
                                        "mode": "none"
                                    }
                                },
                                {"text": "< Back", "type": "back"}
                            ]
                        },
                        {"text": "< Back", "type": "back"}
                    ]
                },
                {
                    "text": "Songs",
                    "type": "menu",
                    "items": [
                        {
                            "text": "Battle Cats theme",
                            "type": "scale_drill",
                            "payload": {
                                "name": "Battle Cats theme",
                                "key_signature": "C_MINOR",
                                "bpm": 96,
                                "notes": [
                                    "C_4", "REST_HALF", "C_4", "E_FLAT_4", "C_4", "F_SHARP_4", "G_4",
                                    "REST_HALF", "C_4", "E_FLAT_4", "F_SHARP_4", "G_4:EIGHTH", "G_4:EIGHTH",
                                    "F_4:EIGHTH", "F_4:EIGHTH", "E_FLAT_4:EIGHTH", "E_FLAT_4:EIGHTH", "C_4:EIGHTH",
                                    "C_4:EIGHTH", "E_FLAT_4:EIGHTH", "C_4", "REST_HALF", "B_FLAT_3", "D_4"
                                ],
                                "mode": "none"
                            }
                        },
                        {
                            "text": "Twinkle Twinkle",
                            "type": "scale_drill",
                            "payload": {
                                "name": "Twinkle Twinkle",
                                "key_signature": "C_MAJOR",
                                "notes": [
                                    "C_4", "C_4", "G_4", "G_4", "A_4", "A_4", "G_4",
                                    "F_4", "F_4", "E_4", "E_4", "D_4", "D_4", "C_4",
                                    "G_4", "G_4", "F_4", "F_4", "E_4", "E_4", "D_4",
                                    "G_4", "G_4", "F_4", "F_4", "E_4", "E_4", "D_4",
                                    "C_4", "C_4", "G_4", "G_4", "A_4", "A_4", "G_4",
                                    "F_4", "F_4", "E_4", "E_4", "D_4", "D_4", "C_4"
                                ],
                                "mode": "none"
                            }
                        },
                        {
                            "text": "Happy Birthday",
                            "type": "scale_drill",
                            "payload": {
                                "name": "Happy Birthday",
                                "key_signature": "F_MAJOR",
                                "notes": [
                                    "C_4", "C_4", "D_4", "C_4", "F_4", "E_4",
                                    "C_4", "C_4", "D_4", "C_4", "G_4", "F_4",
                                    "C_4", "C_4", "C_5", "A_4", "F_4", "E_4", "D_4",
                                    "B_FLAT_4", "B_FLAT_4", "A_4", "F_4", "G_4", "F_4"
                                ],
                                "mode": "none"
                            }
                        },
                        {
                            "text": "Spider Dance",
                            "type": "menu",
                            "items": [
                                {
                                    "text": "Intro",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Spider Dance: Intro",
                                        "key_signature": "G_MAJOR",
                                        "notes": [
                                            "D_5", "A_4", "F_SHARP_4", "D_4", "G_SHARP_4",
                                            "G_4", "F_4", "C_SHARP_4", "C_5", "B_FLAT_3",
                                            "E_4", "C_SHARP_5"
                                        ],
                                        "mode": "none"
                                    }
                                },
                                {
                                    "text": "Theme A",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Spider Dance: Theme A",
                                        "key_signature": "G_MAJOR",
                                        "notes": [
                                            "A_5", "G_5", "D_6", "C_SHARP_6", "B_FLAT_5",
                                            "F_SHARP_5", "D_5", "A_4", "E_5"
                                        ],
                                        "mode": "none"
                                    }
                                },
                                {
                                    "text": "Climax",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Spider Dance: Climax",
                                        "key_signature": "G_MAJOR",
                                        "notes": [
                                            "A_5", "D_6", "G_5", "F_SHARP_5",
                                            "A_FLAT_5", "C_SHARP_5", "A_4", "B_4", "D_5"
                                        ],
                                        "mode": "none"
                                    }
                                },
                                {
                                    "text": "Bridge",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Spider Dance: Bridge",
                                        "key_signature": "G_MAJOR",
                                        "notes": [
                                            "A_5", "F_SHARP_5", "D_5", "G_4", "A_4",
                                            "B_FLAT_4", "F_SHARP_4", "E_5", "C_SHARP_5",
                                            "G_5", "F_5", "C_6", "B_FLAT_5"
                                        ],
                                        "mode": "none"
                                    }
                                },
                                {
                                    "text": "Pattern I",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Spider Dance: Pattern I",
                                        "key_signature": "G_MAJOR",
                                        "notes": ["G_5", "F_SHARP_5", "D_5", "C_SHARP_5"],
                                        "mode": "none"
                                    }
                                },
                                {
                                    "text": "Pattern II",
                                    "type": "scale_drill",
                                    "payload": {
                                        "name": "Spider Dance: Pattern II",
                                        "key_signature": "G_MAJOR",
                                        "notes": ["G_5", "F_SHARP_5", "F_5", "G_SHARP_5", "D_5"],
                                        "mode": "none"
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
                        {"text": "Solarized Dark", "type": "color", "payload": {
                            "name": "Solarized Dark",
                            "bg_color": 0x002B36,
                            "fg_color": 0x93A1A1,
                            "chart_color": 0x93A1A1,
                            "fingering_color": 0xB58900,
                            "drill_note_color": 0x2AA198
                        }},
                        {"text": "Dracula", "type": "color", "payload": {
                            "name": "Dracula",
                            "bg_color": 0x282A36,
                            "fg_color": 0xF8F8F2,
                            "chart_color": 0xF8F8F2,
                            "fingering_color": 0xFF79C6,
                            "drill_note_color": 0x50FA7B
                        }},
                        {"text": "Gruvbox Dark", "type": "color", "payload": {
                            "name": "Gruvbox Dark",
                            "bg_color": 0x282828,
                            "fg_color": 0xEBDBB2,
                            "chart_color": 0xEBDBB2,
                            "fingering_color": 0xFE8019,
                            "drill_note_color": 0xB8BB26
                        }},
                        {"text": "Monokai", "type": "color", "payload": {
                            "name": "Monokai",
                            "bg_color": 0x272822,
                            "fg_color": 0xF8F8F2,
                            "chart_color": 0xF8F8F2,
                            "fingering_color": 0xF92672,
                            "drill_note_color": 0xA6E22E
                        }},
                        {"text": "> Back", "type": "back"}
                    ]
                },
                {
                    "text": "Volume",
                    "type": "volume_settings"
                },
                {"text": "< Back", "type": "back"}
            ]
        }
    ]
}
