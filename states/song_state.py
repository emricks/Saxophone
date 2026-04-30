import asyncio
import audiomp3
import os

from states.play_state import PlayState
from states.state_utils import SelectableList
from hardware.buttons import Buttons


class SongState(PlayState):
    SONG_DIR = "songs"
    AUDIO_BUFFER = bytearray(16384)

    def __init__(self, hardware, payload, config):
        # Initialize PlayState stuff, but don't show its UI yet
        super().__init__(hardware, config, title="Song Mode")
        self.payload = payload
        
        # Setup the selectable list for songs
        self.selectable_list = SelectableList(title="Select Song")
        
        # Load available songs from a directory
        self.songs = self._get_song_list()
        self.menu_items = self.songs + [{"text": "< Back", "type": "back"}]
        self.selectable_list.set_items(self.menu_items, title="Select Song")

        # Initially, show the selectable list UI instead of PlayState UI
        self.hw.display.root_group = self.selectable_list.ui_group

        self.hw.mixer.voice[1].level = config.volume_data.volume

    @staticmethod
    def _get_song_list():
        try:
            files = os.listdir(SongState.SONG_DIR)
            # Create a dictionary entry for each song so it renders nicely
            songs = [{"text": f, "type": "song_item", "file": SongState.SONG_DIR + "/" + f} for f in files if f.endswith(".mp3") and not f.startswith(".")]
            if not songs:
                return [{"text": "No songs found", "type": "info"}]
            return songs
        except Exception as e:
            print(f"Error reading songs: {e}")
            return [{"text": "No songs found", "type": "info"}]

    async def _handle_menu(self):
        """Handles the song selection menu loop. Returns the selected song or None if back was pressed."""
        while True:
            self.hw.update_button_states()
            
            if Buttons.R_1.just_pressed:
                self.selectable_list.move_up()
            elif Buttons.R_2.just_pressed:
                self.selectable_list.move_down()
            elif Buttons.L_SELECT.just_pressed:
                selected_item = self.selectable_list.get_selected_item()
                if not selected_item:
                    continue
                    
                item_type = selected_item.get("type")
                
                if item_type == "back":
                    return None
                elif item_type == "song_item":
                    return selected_item
                elif item_type == "info":
                    pass
                    
            await asyncio.sleep(0.01)

    async def run(self):
        while True:
            # Enter the menu for song listing
            if self.hw.display.root_group != self.selectable_list.ui_group:
                self.hw.display.root_group = self.selectable_list.ui_group
            
            selected_song = await self._handle_menu()
            
            if not selected_song:
                # User pressed back, exit SongState entirely
                return
                
            print(f"Selected song: {selected_song['text']}")
            
            # The file must remain open while playing. We use a 'with' block 
            # to guarantee the file handle is cleaned up when we exit this song.
            with open(selected_song['file'], "rb") as mp3_file:
                decoder = audiomp3.MP3Decoder(mp3_file, SongState.AUDIO_BUFFER)
                self.hw.mixer.voice[1].play(decoder)
                
                # Reset PlayState's running flag in case we played a song previously
                self.is_running = True
                
                # Hand over control to PlayState's run loop.
                await super().run()

                self.hw.mixer.voice[1].stop()