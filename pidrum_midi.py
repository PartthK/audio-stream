import rtmidi
import time
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)

channels = [AnalogIn(ads, pin) for pin in [0,1,2,3]]

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()
if not available_ports:
	print("No MIDI ports found!")

for i, name in enumerate(available_ports):
	if "PiDrums" in name:
		midiout.open_port(i)
		print(f"Connected to MIDI port: {name}")
		break
else:
	print("RTP-MIDI Session not found!")

note_on_flags = [False] * 4
last_hit_time = [0] * 4
note_on_start_time = [0] * 4

notes = [36, 38, 42, 46]
threshold = 0.05
min_note_duration = 0.80
cooldown_time = 0.05
max_voltage = 3.3

try:
	while True:
		current_time = time.time()
		for i, ch in enumerate(channels):
			voltage = ch.voltage
			if voltage > threshold and not note_on_flags[i] and current_time - last_hit_time[i] > cooldown_time:
				velocity = int(min(127, max(1, (voltage / max_voltage) * 127)))
				print(f"Voltage: {voltage: 0.3f}")
				print(f"Velocity: {velocity}")
				midiout.send_message([0x90, notes[i], 100])
				note_on_flags[i] = True
				last_hit_time[i] = current_time
			if note_on_flags[i]:
				if voltage <= threshold and current_time - note_on_start_time[i] >= min_note_duration:
					midiout.send_message([0x80, notes[i], 0])
					note_on_flags[i] = False
		time.sleep(0.003)

except KeyboardInterrupt:
	print("Exiting...")
finally:
	for i, flag in enumerate(note_on_flags):
		if flag:
			midiout.send_message([0x80, notes[i], 0])
	midiout.close_port()
