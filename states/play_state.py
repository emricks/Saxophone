import asyncio
import bitmaptools
import displayio
import terminalio
import adafruit_imageload
from adafruit_display_text import label

from composer.key_signature import KeySignature, KeySignatures
from composer.notes import Duration, Notes as ComposerNotes, note_for_key
from composer.staff import Staff
from data.config import Config
from hardware.buttons import Buttons
from hardware.saxophone import SaxHardware


class PlayState:
    STAFF_WIDTH = 212
    def __init__(self, hardware, config: Config, title="Free Play", key_signature: KeySignature = KeySignatures.C_MAJOR):
        self.hw = hardware
        self.is_running = True
        self.current_note_playing = None

        self.ui_group = displayio.Group()
        self.hw.mixer.voice[0].level = config.volume_data.volume
        self.hw.mixer.voice[1].level = config.volume_data.volume

        # Background
        color_bitmap = displayio.Bitmap(320, 240, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = config.color_data.bg_color
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self.ui_group.append(bg_sprite)

        # Drill Name along the top
        self.title_label = label.Label(
            terminalio.FONT,
            text=title,
            color=config.color_data.fg_color,
            scale=1,
            x=10,
            y=15
        )
        self.ui_group.append(self.title_label)

        # Staff
        self.staff = Staff(width=PlayState.STAFF_WIDTH, config=config, key_signature=key_signature)
        self.staff.x = 0
        self.staff.y = (240 - Staff.HEIGHT) // 2
        self.ui_group.append(self.staff)

        # load chart
        chart_bitmap, chart_palette = adafruit_imageload.load(
            "data/img/sax_fingering_blank.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        chart_palette.make_transparent(1)
        chart_palette[0] = config.color_data.chart_color
        chart_palette[2] = config.color_data.fingering_color
        self.chart_sprite = displayio.TileGrid(chart_bitmap, pixel_shader=chart_palette, x=210, y=0)

        self.blit_bitmap, blit_palette = adafruit_imageload.load(
            "data/img/sax_fingering_blit.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        blit_palette[2] = config.color_data.fingering_color
        self.unblit_bitmap, unblit_palette = adafruit_imageload.load(
            "data/img/sax_fingering_unblit.png",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        unblit_palette[0] = config.color_data.chart_color

    async def hide_notes(self):
        await asyncio.sleep(SaxHardware.NOTE_RELEASE_TIME)
        self.staff.update_sequence([])

    def update_chart(self):
        for button in Buttons.ALL:
            if button.just_pressed and button.bounding_box is not None:
                box = button.bounding_box
                bitmaptools.blit(self.chart_sprite.bitmap, self.blit_bitmap, x=box.x0, y=box.y0, x1=0, y1=0,
                                 x2=box.calculate_width(),
                                 y2=box.calculate_height(),
                                 skip_dest_index=1)
            elif button.just_released and button.bounding_box is not None:
                box = button.bounding_box
                bitmaptools.blit(self.chart_sprite.bitmap, self.unblit_bitmap, x=box.x0, y=box.y0, x1=0, y1=0,
                                 x2=box.calculate_width(),
                                 y2=box.calculate_height(),
                                 skip_dest_index=1)

    async def run(self):
        if self.hw.display.root_group != self.ui_group:
            self.hw.display.root_group = self.ui_group

        if self.chart_sprite not in self.ui_group:
            self.ui_group.append(self.chart_sprite)

        self.current_note_playing = None
        await self.hw.stop_note()
        await self.hide_notes()

        while self.is_running:
            self.hw.update_button_states()
            self.update_chart()

            if Buttons.L_SELECT.just_pressed:
                self.is_running = False
                break

            target_note = self.hw.get_current_note()
            await self.process_playing_note(target_note)
            await asyncio.sleep(0.001)

        await self.hw.stop_note()

    async def process_playing_note(self, note):
        breathing = self.hw.breath_sensor.breath_sensor_triggered
        if note is None or not breathing:
            if self.current_note_playing is not None:
                await self.hw.stop_note()
                await self.hide_notes()
                self.current_note_playing = None
                self.hw.display.refresh()
            return

        if note != self.current_note_playing:
            await self.hw.stop_note()
            await self.hide_notes()

            if note is not None:
                self.hw.play_note(note.midi_number)
                composer_note = note_for_key(note.midi_number, self.staff.key_signature)
                if composer_note is not None:
                    self.staff.show_note(composer_note, Duration.HALF)

            self.current_note_playing = note
            self.hw.display.refresh()

    async def clear_specific_fingering(self, fingering):
        if fingering:
            for button in fingering:
                if button.bounding_box:
                    box = button.bounding_box
                    bitmaptools.blit(self.chart_sprite.bitmap, self.unblit_bitmap, x=box.x0, y=box.y0, x1=0, y1=0,
                                     x2=box.calculate_width(),
                                     y2=box.calculate_height(),
                                     skip_dest_index=1)
                    await asyncio.sleep(0.001)

    async def blit_specific_fingering(self, fingering):
        if fingering:
            for button in fingering:
                if button.bounding_box:
                    box = button.bounding_box
                    bitmaptools.blit(self.chart_sprite.bitmap, self.blit_bitmap, x=box.x0, y=box.y0, x1=0, y1=0,
                                     x2=box.calculate_width(),
                                     y2=box.calculate_height(),
                                     skip_dest_index=1)
                    await asyncio.sleep(0.001)