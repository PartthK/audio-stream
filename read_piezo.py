import sys
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)

ads1 = ADS.ADS1115(i2c, address=0x48)
ads2 = ADS.ADS1115(i2c, address=0x49)
ads1.data_rate = 860
ads1.gain = 1
ads2.data_rate = 860
ads2.gain = 1 
chan0 = AnalogIn(ads1, 0)
chan1 = AnalogIn(ads1, 1)
chan2 = AnalogIn(ads1, 2)
chan3 = AnalogIn(ads1, 3)
chan4 = AnalogIn(ads2, 0)
chan5 = AnalogIn(ads2, 1)
chan6 = AnalogIn(ads2, 2)
chan7 = AnalogIn(ads2, 3)
print(f"Start")
while True:
	try:
		v0 = abs(chan0.voltage)
		v1 = abs(chan1.voltage)
		v2 = abs(chan2.voltage)
		v3 = abs(chan3.voltage)
		v4 = abs(chan4.voltage)
		v5 = abs(chan5.voltage)
		#v6 = abs(chan6.voltage)
		v7 = abs(chan7.voltage)
		if v0 > 0.01:
			print(f"Voltage on A0_1: {v0:.3f}V")
		if v1 > 0.01:
			print(f"Voltage on A1_1: {v1:.3f}V")
		if v2 > 0.01:
			print(f"Voltage on A2_1: {v2:.3f}V")
		if v3 > 0.01:
			print(f"Voltage on A3_1: {v3:.3f}V")
		if v4 > 0.01:
			print(f"Voltage on A0_2: {v4:.3f}V")
		if v5 > 0.01:
			print(f"Voltage on A1_2: {v5:.3f}V")
		#if v6 > 0.01:
			#print(f"Voltage on A2_2: {v6:.3f}V")
		if v7 > 0.01:
			print(f"Voltage on A3_2: {v7:.3f}V")
		time.sleep(0.1)
	except KeyboardInterrupt:
		sys.exit()
	except:
		continue
