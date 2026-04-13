import asyncio
import time

import adafruit_bmp3xx


class BreathSensor:
    # breath sensor constants
    THRESHOLD = 0.3# hPa change required to trigger breath sensor
    NOISE_FLOOR = THRESHOLD/2  # Changes smaller than this are treated as drift (baseline updates)
    LEARNING_RATE = 0.005  # How quickly the baseline follows drift (e.g. 0.01 = 1%)
    CHECK_INTERVAL = .08 # how often to check if sensor is activated

    def __init__(self, i2c):
        self.breath_sensor_triggered = False

        self.breath_sensor = adafruit_bmp3xx.BMP3XX_I2C(i2c)
        self.breath_sensor.pressure_oversampling = 8
        self.breath_sensor.filter_coefficient = 2
        self.initial_baseline = self.__get_breath_sensor_baseline__()
        self.baseline_offset = 0.0
        self.learning_baseline = True

    @property
    def breath_sensor_baseline(self):
        return self.initial_baseline + self.baseline_offset

    def __get_breath_sensor_baseline__(self):
        """Takes multiple readings to filter out sensor noise for a solid baseline."""
        readings = []
        for _ in range(10):
            readings.append(self.breath_sensor.pressure)
            time.sleep(0.05)
        avg_p = sum(readings) / len(readings)
        print(f"New baseline established: {avg_p:.4f} hPa")
        return avg_p

    def __update_breath_sensor_baseline__(self, current_offset):
        if self.learning_baseline:
            self.baseline_offset += BreathSensor.LEARNING_RATE * (current_offset - self.baseline_offset)

    async def __monitor_breath_sensor__(self):
        while True:
            current_pressure = self.breath_sensor.pressure
            current_offset = current_pressure - self.initial_baseline
            diff = self.baseline_offset - current_offset
            # Update baseline air pressure if we detect minor fluctuation or any negative drift
            if not self.breath_sensor_triggered:
                self.__update_breath_sensor_baseline__(current_offset)
            self.breath_sensor_triggered = diff > BreathSensor.THRESHOLD
            #DEBUG
            #print(f"Breath Sensor Triggered: {self.breath_sensor_triggered}, diff: {diff}, baseline: {self.breath_sensor_baseline}, current: {current_pressure}")
            await asyncio.sleep(BreathSensor.CHECK_INTERVAL)

    async def start(self):
        asyncio.create_task(self.__monitor_breath_sensor__())
