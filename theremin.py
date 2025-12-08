import leap
import time
import rtmidi
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, CONTROL_CHANGE

MIN_PITCH_DISTANCE = -150
MAX_PITCH_DISTANCE = 150
MIN_VOLUME_DISTANCE = 70
MAX_VOLUME_DISTANCE = 250

LOWEST_PITCH = 36 #C2
HIGHEST_PITCH = 96 #C7
LOWEST_VOLUME = 0
HIGHEST_VOLUME = 127

lastPitch = 0
zPosition = 0
yPosition = 0

midi_out = rtmidi.MidiOut()
available_ports = midi_out.get_ports()
for i, port in enumerate(available_ports):
    print(f"Available MIDI Port {i}: {port}")
    if "Noah" in port:
        midi_out.open_port(i)
        print(f"Opened MIDI port: {port}")

class ThereminListener(leap.Listener):
    def on_connection_event(self, event):
        print("Connected")

    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()

        print(f"Found device {info.serial}")

    def on_tracking_event(self, event):
        global lastPitch, zPosition, yPosition

        if len(event.hands) == 0:
            midi_note = [NOTE_OFF, lastPitch, LOWEST_VOLUME] #note off
            midi_out.send_message(midi_note)
            return

        for hand in event.hands:
            if str(hand.type) == "HandType.Right":
                #print(f" Theremin Right Hand Pitch - Palm Z: {hand.palm.position.z}")
                zPosition = min(max(hand.palm.position.z, MIN_PITCH_DISTANCE), MAX_PITCH_DISTANCE)

            elif str(hand.type) == "HandType.Left":
                #print(f" Theremin Left Hand Volume - Palm Y: {hand.palm.position.y}")
                yPosition = min(max(hand.palm.position.y, MIN_VOLUME_DISTANCE), MAX_VOLUME_DISTANCE)

        normZ = (MAX_PITCH_DISTANCE - zPosition) / (MAX_PITCH_DISTANCE - MIN_PITCH_DISTANCE)  #normalize form 0 to 1
        pitch = int(LOWEST_PITCH + normZ * (HIGHEST_PITCH - LOWEST_PITCH))  #scale 
        normY = (yPosition - MIN_VOLUME_DISTANCE) / (MAX_VOLUME_DISTANCE - MIN_VOLUME_DISTANCE) 
        volume = int(normY * HIGHEST_VOLUME)

        midi_note = [NOTE_ON, pitch, volume] #set pitch and set inital volume
        midi_volume = [CONTROL_CHANGE, 11, volume] #change volume during note

        midi_out.send_message(midi_note)
        lastPitch = pitch
        
        midi_out.send_message(midi_volume)

def main():
    my_listener = ThereminListener()
    connection = leap.Connection()
    connection.add_listener(my_listener)

    running = True

    try:
        with connection.open():
            connection.set_tracking_mode(leap.TrackingMode.Desktop)
            while running:
                pass
    except KeyboardInterrupt:
        print("Exiting...")
        running = False
    finally:
        for i in range(1,128):
            midi_out.send_message([NOTE_OFF, i, 0]) #note off on exit
        connection.remove_listener(my_listener)
        midi_out.close_port()

if __name__ == "__main__":
    main()