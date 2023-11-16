import asyncio
import json
import numpy as np
from pythonosc import udp_client, osc_server, osc_message_builder
import time
import threading
import tkinter as tk
from tkinter import ttk
import sounddevice as sd 
import websockets as ws
from websockets.legacy.server import WebSocketServerProtocol

def devices():
  devs = sd.query_devices()
  names = []
  for device in devs: 
    names.append(device.get('name'))
  return names

def start_stream(input_device: str):
    with sd.InputStream(device=input_device, channels=1, samplerate=44100, callback=record) as stream:
        print("Stream started")
        while True:
            sd.sleep(1000)

def send_udp(amp: float, client: udp_client.SimpleUDPClient):
    try:
     client.send_message("/amp", float(amp))
    except Exception as e:
     status.delete('1.0', tk.END)
     status.insert(tk.END, f"Client log: {e}", "center")

async def send_ws(amp: float, client):
    try:
      msg = osc_message_builder.OscMessageBuilder(address = "/amp")
      msg.add_arg(float(amp))
      msg = msg.build()
      bytes = msg.dgram
      await client.send(bytes)
    except Exception as e:
      status.delete('1.0', tk.END)
      status.insert(tk.END, f"Client log: {e}", "center") 

CLIENT = None

def record(indata, frames, time, status):
   global CLIENT
   data = np.linalg.norm(indata)
   if isinstance(CLIENT, udp_client.SimpleUDPClient):
    send_udp(data, CLIENT)
   elif isinstance(CLIENT, WebSocketServerProtocol):
    msg = osc_message_builder.OscMessageBuilder(address = "/amp")
    msg.add_arg(float(data))
    osc_m = msg.build()
    bytes = osc_m.dgram

async def ws_loop(client):
  while True:
   await client.send(b'Hello world!')

def config(mode: str, host: str, port: int, input_device: str):
 global CLIENT
 match mode:
  case 'UDP':
    CLIENT = udp_client.SimpleUDPClient(host, port)
  case 'WebSocket':
    async def handler(websocket,path):
        global CLIENT
        ip, port = websocket.remote_address
        CLIENT = websocket
        await ws_loop(websocket)
    start_server = ws.serve(handler, host, port) 
    asyncio.get_event_loop().run_until_complete(start_server)
    threading.Thread(target=asyncio.get_event_loop().run_forever).start()  
 threading.Thread(target=start_stream, args=(input_device,)).start()
 status.delete('1.0', tk.END)
 status.insert(tk.END, f"Sending to {mode} {host} and port {port}", "center")
 status.pack()


app = tk.Tk()

#FPS = tk.StringVar()
MODE = tk.StringVar()
HOST = tk.StringVar() 
PORT = tk.StringVar()
DEV = tk.StringVar()

devsList = tk.ttk.Combobox(app, values=devices(), textvariable=DEV, state="readonly")
ipLabel = tk.Label(app, text="IP (Outcoming)") 
ip = tk.Entry(app, textvariable=HOST)
portLabel = tk.Label(app, text="Port (Outcoming)") 
port = tk.Entry(app, textvariable=PORT) 
status = tk.Text(app, height=3, width=60, bg='gray')
start_button = tk.Button(app, text="Start sending", command=lambda: config(MODE.get(), HOST.get(), int(PORT.get()), DEV.get()))
#fps_label = tk.Label(text="FPS")
#fps_settings = tk.Entry(app, textvariable=FPS, width=4, justify="center")
server_type_settings = tk.ttk.Combobox(app, values=['UDP', 'WebSocket'], state="readonly", textvariable=MODE, width=9, justify="center")

ip.insert(tk.END,'127.0.0.1')
devsList.set(devices()[0])
status.tag_configure("center", justify='center')
#fps_settings.insert(tk.END,'60')
server_type_settings.set('UDP')

devsList.pack()
ipLabel.pack()
ip.pack()
portLabel.pack()
port.pack()
start_button.pack()
#fps_label.pack()
#fps_settings.pack()
server_type_settings.pack()

# Získanie rozmerov obrazovky
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

window_width = 500
window_height = 250
app.geometry(f"{window_width}x{window_height}")

# Výpočet súradníc pre umiestnenie okna do stredu obrazovky
center_x = int((screen_width - window_width) / 2)
center_y = int((screen_height - window_height) / 2)

# Umiestnenie okna do stredu obrazovky
app.geometry(f"+{center_x}+{center_y}")

app.title("Amp Sender") 
app.mainloop() 