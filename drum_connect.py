import rtmidi
import time
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from fastapi import Body

class Pad(BaseModel):
    id: int
    enabled: bool
    note: int
    threshold: float
    lastHit: int = 0


midi_out = rtmidi.MidiOut()
ports = midi_out.get_ports()
print("Available MIDI Ports:", ports)

connected = False
for i, name in enumerate(ports):
    if "PiDrums" in name:
        midi_out.open_port(i)
        print(f"Connected to MIDI port: {name}")
        connected = True
        break

if not connected:
    print("❌ RTP-MIDI Session 'PiDrums' not found!")
else:
    print("✅ MIDI Ready")

class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)
        print("App connected:", websocket.client)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, msg: dict):
        for ws in list(self.active):
            try:
                await ws.send_json(msg)
            except:
                self.disconnect(ws)


manager = ConnectionManager()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


pads: List[Pad] = [
    Pad(
        id=i,
        enabled=True,
        note=[36, 38, 41, 45, 42, 46, 49, 51][i],
        threshold=0.05
    )
    for i in range(8)
]


i2c = busio.I2C(board.SCL, board.SDA)
ads1 = ADS1115(i2c, address=0x48)
channels1 = [AnalogIn(ads1, pin) for pin in [0, 1, 2, 3]]
ads2 = ADS1115(i2c, address=0x49)
channels2 = [AnalogIn(ads2, pin) for pin in [0, 1, 2, 3]]

channels = channels1 + channels2

def midi_on(note: int, vel: int):
    midi_out.send_message([0x90, note, 127])


def midi_off(note: int):
    midi_out.send_message([0x80, note, 0])


@app.get("/pads")
async def get_pads():
    return pads


class PadUpdate(BaseModel):
    enabled: bool
    note: int
    threshold: float


@app.post("/pads/{pad_id}/update")
async def update_pad(pad_id: int, pad_update: PadUpdate):
	for p in pads:
		if p.id == pad_id:
            		p.enabled = pad_update.enabled
            		p.note = pad_update.note
            		p.threshold = pad_update.threshold

            		await manager.broadcast(p.model_dump())
            		return p

	return {"error": "Pad not found"}


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if data["action"] == "update":
                pad = pads[data["pad_id"]]
                pad.enabled = data["enabled"]
                pad.note = data["note"]
                pad.threshold = data["threshold"]

                await manager.broadcast(pad.dict())

    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def piezo_loop():
    note_on = [False] * 8
    last_hit = [0] * 8
    note_start = [0] * 8

    cooldown = 0.05
    min_note_dur = 0.80
    max_v = 0.3

    while True:
        now = time.time()

        for i, ch in enumerate(channels):
            pad = pads[i]
            voltage = ch.voltage

            if (pad.enabled and voltage > pad.threshold and not note_on[i] and now - last_hit[i] > cooldown):
                vel = int(min(127, max(1, (voltage / max_v) * 127)))
                print(f"Pad {i} Voltage={voltage:.3f} Velocity={vel}")

                midi_on(pad.note, vel)
                note_on[i] = True
                last_hit[i] = now
                note_start[i] = now

                pad.lastHit = int(time.time() * 1_000_000)
                await manager.broadcast(pad.model_dump())

            if note_on[i] and (voltage <= pad.threshold and now - note_start[i] >= min_note_dur):
                    midi_off(pad.note)
                    note_on[i] = False

        await asyncio.sleep(0.003)


# ---------------------------
# Run Uvicorn
# ---------------------------
import uvicorn
from uvicorn.config import Config
from uvicorn.server import Server

async def main():
	loop = asyncio.get_event_loop()
	loop.create_task(piezo_loop())

	config = Config(
		app=app,
		host="0.0.0.0",
		port=8000,
		loop="asyncio",
	)
	server = Server(config)
	await server.serve()

if __name__ == "__main__":
	asyncio.run(main())
