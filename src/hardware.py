# hardware.py
import array
import board
import busio
import digitalio
import displayio
import fourwire
import adafruit_ili9341
import keypad
import audiobusio
import synthio
import audiomixer


class SaxHardware:
    def __init__(self):
        displayio.release_displays()

        # --- Display Setup (Verified Working) ---
        self.spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
        self.tft_cs = board.MISO
        self.tft_dc = board.RX
        self.tft_rst = board.D4

        self.backlight = digitalio.DigitalInOut(board.TX)
        self.backlight.direction = digitalio.Direction.OUTPUT
        self.backlight.value = True

        self.display_bus = fourwire.FourWire(
            self.spi, command=self.tft_dc, chip_select=self.tft_cs, reset=self.tft_rst, baudrate=62500000
        )
        self.display = adafruit_ili9341.ILI9341(self.display_bus, width=320, height=240)

        # --- Audio Setup ---
        # 1. Turn on the Prop-Maker's I2S Amplifier
        self.audio_enable = digitalio.DigitalInOut(board.EXTERNAL_POWER)
        self.audio_enable.direction = digitalio.Direction.OUTPUT
        self.audio_enable.value = True

        # 2. Setup the I2S Bus
        self.audio = audiobusio.I2SOut(
            bit_clock=board.I2S_BIT_CLOCK,
            word_select=board.I2S_WORD_SELECT,
            data=board.I2S_DATA
        )

        # 3. Create the Mixer and play it on the audio bus
        self.mixer = audiomixer.Mixer(
            voice_count=1,
            sample_rate=22050,
            channel_count=1,
            bits_per_sample=16,
            samples_signed=True
        )
        self.audio.play(self.mixer)

        # 4. Initialize the Synthesizer and attach it to the mixer
        self.synth = synthio.Synthesizer(sample_rate=22050)
        # type: ignore (or # noinspection PyTypeChecker)
        self.mixer.voice[0].play(self.synth)

        # 5. Set Master Volume
        self.mixer.voice[0].level = 0.3

        # 6. The Breath (Envelope)
        self.sax_envelope = synthio.Envelope(
            attack_time=0.1,  # 100ms fade-in
            decay_time=0.0,
            release_time=0.15,  # 150ms fade-out
            attack_level=1.0,
            sustain_level=1.0
        )

        # 7. The Tone (Waveform)
        self.sax_waveform = self.load_wav_buffer("data/audio/AKWF_altosax_0001.wav")

        # --- Navigation Buttons ---
        # Wiring: Connect buttons from these pins to GND
        self.nav_pins = (board.D11, board.D13, board.D12)

        # 2. Dynamically assign the logical roles based on the pin's actual position
        self.BTN_UP = self.nav_pins.index(board.D11)
        self.BTN_SELECT = self.nav_pins.index(board.D13)
        self.BTN_DOWN = self.nav_pins.index(board.D12)

        self.keys = keypad.Keys(self.nav_pins, value_when_pressed=False, pull=True)
        self.key_states = [False] * len(self.nav_pins)

    def stop_note(self):
            """Releases all active notes to trigger the fade-out envelope."""
            self.synth.release_all()

    def play_note(self, midi_number):
        """Converts a MIDI integer to Hertz and plays it with the sax waveform."""
        freq = 440.0 * (2.0 ** ((midi_number - 69) / 12))
        note = synthio.Note(
            frequency=freq,
            envelope=self.sax_envelope,
            waveform=self.sax_waveform
        )
        self.synth.press(note)

    def load_wav_buffer(self, filename):
        """Hacks a standard 16-bit mono WAV file directly into a raw array."""
        try:
            with open(filename, "rb") as f:
                f.seek(44)  # Skip the 44-byte standard header

                # The AKWF documentation states the audio is exactly 600 samples.
                # 600 samples * 2 bytes (16-bit) = 1200 bytes.
                raw_bytes = f.read(1200)

                return array.array('h', raw_bytes)
        except Exception as e:
            print(f"Failed to load {filename}: {e}")
            return None

    def get_button_event(self):
        """Returns the next event and updates the live key states."""
        event = self.keys.events.get()
        if event:
            # Update our live tracking array (True if held, False if released)
            self.key_states[event.key_number] = event.pressed
        return event