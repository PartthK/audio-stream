How to connect the Pi to Macbook (Network)
Ensure Mac and Pi are on the same Wifi 

ON THE PI:
	Enter Desktop/py virtual environment (source env/bin/activate) and run the rtpmidi server “./run_rtpmidid.sh”

ON MAC:
	_Open Audio Midi Setup_
	Click Network Globe (top right)
	Create Session and **NAME SESSION “PiDrums”.** Activate with check mark on left
	Underneath in 'Sessions and Directories', you should see “RaspberryPiMidi”
	Click and connect to “RaspberryPiMidi” to add it to the PiDrums session

	_Open Garageband_
	Select software instrument – on left side find drums and choose a drum instrument
  
ON PI:
	Run “python3 pidrum_midi.py” while in virtual environment

Ensure orange live monitoring button is clicked in GarageBand channel. Make sure Mac volume is up
When piezo disks are tapped, corresponding sound plays in Garageband

ON PI (when done):
	Kill rtpmidid
	“./kill_rtpmidid.sh”

Shut down Pi: sudo shutdown

