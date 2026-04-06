import asyncio
import time

import adafruit_bmp3xx


class BreathSensor:
    # breath sensor constants
    THRESHOLD = 0.04  # hPa change required to trigger breath sensor
    NOISE_FLOOR = THRESHOLD / 2  # Changes smaller than this are treated as drift (baseline updates)
    LEARNING_RATE = 0.01  # How quickly the baseline follows drift (0.01 = 1%)
    CHECK_INTERVAL = .05 # how often to check if sensor is activated

    def __init__(self, i2c):
        self.breath_sensor_triggered = False

        self.breath_sensor = adafruit_bmp3xx.BMP3XX_I2C(i2c)
        self.breath_sensor.pressure_oversampling = 8
        self.breath_sensor.filter_coefficient = 2
        self.breath_sensor_baseline = self.__get_breath_sensor_baseline__()

    def __get_breath_sensor_baseline__(self):
        """Takes multiple readings to filter out sensor noise for a solid baseline."""
        readings = []
        for _ in range(10):
            readings.append(self.breath_sensor.pressure)
            time.sleep(0.05)
        avg_p = sum(readings) / len(readings)
        print(f"New baseline established: {avg_p:.2f} hPa")
        return avg_p

    def __update_breath_sensor_baseline__(self):
        current = self.breath_sensor.pressure
        self.breath_sensor_baseline = (self.breath_sensor_baseline * (1 - BreathSensor.LEARNING_RATE)) + (current * BreathSensor.LEARNING_RATE)

    async def __monitor_breath_sensor__(self):
        while True:
            current_pressure = self.breath_sensor.pressure
            diff = self.breath_sensor_baseline - current_pressure
            # Update baseline air pressure if we detect minor fluctuation
            if abs(diff) < BreathSensor.NOISE_FLOOR:
                self.__update_breath_sensor_baseline__()
            self.breath_sensor_triggered = diff > BreathSensor.THRESHOLD
            #DEBUG
            #print(f"Breath Sensor Triggered: {self.breath_sensor_triggered}, diff: {diff}, baseline: {self.breath_sensor_baseline}, current: {current_pressure}")
            await asyncio.sleep(BreathSensor.CHECK_INTERVAL)

    async def start(self):
        asyncio.create_task(self.__monitor_breath_sensor__())