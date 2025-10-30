import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c)
ads.data_rate = 860
ads.gain = 1
chan = AnalogIn(ads, 0)

while True:
	v = abs(chan.voltage)
	if v > 1.0:
		print(f"MQ-135 Voltage: {v}V")
	time.sleep(0.0005)
