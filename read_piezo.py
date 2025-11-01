import sys
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c)
ads.data_rate = 860
ads.gain = 1
chan0 = AnalogIn(ads, 0)
chan1 = AnalogIn(ads, 1)
chan2 = AnalogIn(ads, 2)
chan3 = AnalogIn(ads, 3)
print(f"Start")
while True:
	try:
		v0 = abs(chan0.voltage)
		v1 = abs(chan1.voltage)
		v2 = abs(chan2.voltage)
		v3 = abs(chan3.voltage)
		if v0 > 0.01:
			print(f"Voltage on A0: {v0:.3f}V")
		if v1 > 0.01:
			print(f"Voltage on A1: {v1:.3f}V")
		if v2 > 0.01:
			print(f"Voltage on A2: {v2:.3f}V")
		if v3 > 0.01:
			print(f"Voltage on A3: {v3:.3f}V")
		time.sleep(0.005)
	except KeyboardInterrupt:
		sys.exit()
	except:
		continue
