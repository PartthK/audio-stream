**OVERVIEW**

Audio Stream

PiDrums is a Raspberry-Pi-powered electronic drum system that sends MIDI notes to a Mac running Garageband

It includes:
* Real-time piezo drum pad detection
* A full FastAPI backend running on the Pi
* WebSocket live pad updates
* A custom iOS app for pad configuration (enabling, threshold, MIDI note assignment)
* RTP-MIDI networking between the Pi and Mac
* And future VL53L1X digital theremin sensors also sent to garageband

**Network and Midi Setup (Pi - Mac)**

A. Ensure Both Devices are on the same Wi-Fi Network

**Starting MIDI on the Raspberry Pi**

Enter virtual environment:

	cd ~/Desktop/py
	
	source env/bin/activate


Run the RTP-MIDI server (This launches the background RTP-MIDI daemon that allows the pi to act as a MIDI device on the network):

	./run_rtpmidid.sh

**Configure MIDI on the Mac**

Open "Audio MIDI Setup" on macOS

	Search Audio MIDI Setup
	
	In the top menu, select Window->Show MIDI Setup
	
	Click the Network globe icon (upper right)


Create Network MIDI session

	Press + to make a new session
	
	Name it: PiDrums (MUST BE THIS EXACT NAME TO CONNECT PI)
	
	Ensure "Enabled" (checkbox on left) is ON


Connect the Pi

	Under "Sessions and Directories" on the right, 
	
		click on "RaspberryPiMidi" and click connect
		
		RaspberryPiMidi should now be listed under Participants  -> PiDrums session
		

**GarageBand Setup**

Open Garageband

Create a Software Instrument Track

On the left, selected Drum Kit

Enable Input Monitoring (orange speaker button on track)

Confirm Mac volume is up


**Running the Drum Code on the Pi**

Inside the virtual environment on the Pi run:

	python3 drum_connect.py


The Pi will now:

	Read piezo disks
	
	Stream MIDI into GarageBand
	
	Serve live pad data to the iOS app over WebSocket
	

MUST RESTART GARAGEBAND EVERY TIME THE PROGRAM IS RE-RUN FROM THE PI

  
**Using the iOS App**

The iOS app lets you:

	View all pads (Auto-updated live via WebSocket)
	
	Toggle pad enabled/disabled
	
	Change each pad's MIDI note
	
	Adjust detection thresholds
	

Make sure the simulator (on Mac) or iPhone in on the same Wi-Fi network as the Pi

	The app automatically connects to:
	
		http://10.0.0.24:8000 (http://<raspberry-pi-ip>:8000)
		

**When Finished**

Stop RTP-MIDI on Raspberry Pi

	./kill_rtpmidid.sh
	

Shut down Pi

	sudo shutdown -h now
	

**Troubleshooting**

Make sure the Pi sees the Analog-to-Digital converters

	sudo i2c detect -y 1
	
		Should see the 2 addresses of the ADS1115s
		

If you don't see the RaspberryPiMidi on Mac Network Screen

	Ensure Pi is on Wi-Fi (Must be able to see other devices, be on private network)
	
	Ensure rtpmidid is running
	
	Try restarting Audio MIDI setup on Mac
	
	Ensure firewall is off on Mac for incoming connections
	

If no sound coming through in GarageBand:

	Restart GarageBand
	
	Make sure Input Monitoring (orang speaker icon) is enabled
	
	Make sure no other app is using the MIDI session
	
	Check that the Pi is actually sending MIDI messages (via print logs)
	

**Individual Testing**

Use pidrum_midi.py to test if piezo disks can send to GarageBand

Use read_piezo.py to see if the Pi is reading hits from piezo disks


**System Block Diagram**


                ┌────────────────────────────┐
                │          iOS App	         │
                │  • Pad settings (note,     │
                │    threshold, enable)      │
                │  • Receives live hits      │
                │    (flashes) via WebSocket │
                └────────────┬───────────────┘
                             │ HTTP + WS
                             │
                             ▼
        ┌─────────────────────────────────────────────┐
        │               Raspberry Pi                  │
        │─────────────────────────────────────────────│
        │   FastAPI Server                            │
        │   • /pads (GET)                             │
        │   • /pads/{id}/update (POST)                │
        │   • WebSocket broadcast                     │
        │                                             │
        │   Sensor Processing                         │
        │   • 8 Piezo ADC inputs (ADS1115 @ 0x48/49)  │
        │   • Threshold detection                     │
        │   • Generates MIDI notes                    │
        │                                             │
        │   RTP-MIDI (rtpmidid)                       │
        │   • Sends MIDI over Wi-Fi                   │
        └───────────────┬────────────────────────────┘
                        │ Network MIDI (RTP-MIDI)
                        ▼									
          ┌────────────────────────────────────┐         
          │         MacBook (macOS)            │
          │────────────────────────────────────│
          │ Theremin						   |
		  |	 • Leap Motion API                 |
		  |									   |
		  |	Audio MIDI Setup                   │
          │  • Network Session "PiDrums"       │
          │  • Participant: RaspberryPiMidi    |
	      │  • Advertise as MIDI device via    |
		  |    bluetooth					   |
          │                                    |
          │ GarageBand                         │
          │  • Software Instrument Track       │
          │  • Line 1 = Drumset (Piezo pads)   │
          │  • Input Monitoring ON             │
          └────────────────────────────────────┘
		                │ Bluetooth
                        ▼									
          ┌────────────────────────────────────┐         
          │         iPhone (IOS)               │
          │────────────────────────────────────│
          │ GarageBand                         │
          │  • Software Instrument Track       │
          │  • Line 1 = Theremin               │
          │  • Input Monitoring ON             │
          └────────────────────────────────────┘

