import asyncio
import numpy as np
from pythonosc import udp_client, osc_server, osc_message_builder
import threading
import tkinter as tk
from tkinter import ttk
import sounddevice as sd 
import websockets as ws

def devices():
  devs = sd.query_devices()
  names = []
  for device in devs: 
    names.append(device.get('name'))
  return names

def record(input_device: str):
   sample = sd.rec(1, 44100, 1, np.float32, device=input_device)
   sd.wait()
   amp = sample[0][0]
   # amp is the amplitude to be sent
   return amp

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

def udp_loop(input_device: str, client: udp_client.SimpleUDPClient, speed: float):
  while True:
    amp = record(input_device)
    send_udp(amp, client)

async def ws_loop(input_device: str, client, speed: float):
    while True:
        amp = record(input_device)
        await send_ws(amp, client)

def config(mode: str, host: str, port: int, speed: float, input_device: str):
 try:
   match mode:
    case 'UDP':
     client = udp_client.SimpleUDPClient(host, port)
     threading.Thread(target=udp_loop, args=(input_device, client, 1/speed)).start()
    case 'WebSocket':
     async def handler(websocket,path):
        ip, port = websocket.remote_address
        status.insert(tk.END, f"\nClient connected from {ip} and port {port}", "center")
        try:
         await ws_loop(input_device, websocket, 1/speed)
        except Exception as e:
         status.delete('1.0', tk.END)
         status.insert(tk.END, f"Server log: {e}", "center")
     serve = ws.serve(handler, host, port)
     asyncio.get_event_loop().run_until_complete(serve)
     threading.Thread(target=asyncio.get_event_loop().run_forever).start()

   status.delete('1.0', tk.END)
   status.insert(tk.END, f"Sending to {MODE.get()} {HOST.get()} and port {PORT.get()}", "center")
   status.pack()
 except ValueError as e:
    status.delete('1.0', tk.END)
    status.insert(tk.END, e, "center")


app = tk.Tk()

FPS = tk.StringVar()
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
start_button = tk.Button(app, text="Start sending", command=lambda: config(MODE.get(), HOST.get(), int(PORT.get()), float(FPS.get()), DEV.get()))
fps_label = tk.Label(text="FPS")
fps_settings = tk.Entry(app, textvariable=FPS, width=4, justify="center")
server_type_settings = tk.ttk.Combobox(app, values=['UDP', 'WebSocket'], state="readonly", textvariable=MODE, width=9, justify="center")

ip.insert(tk.END,'127.0.0.1')
devsList.set(devices()[0])
status.tag_configure("center", justify='center')
fps_settings.insert(tk.END,'60')
server_type_settings.set('UDP')

devsList.pack()
ipLabel.pack()
ip.pack()
portLabel.pack()
port.pack()
start_button.pack()
fps_label.pack()
fps_settings.pack()
server_type_settings.pack()

# Získanie rozmerov obrazovky
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

window_width = 500
window_height = 300
app.geometry(f"{window_width}x{window_height}")

# Výpočet súradníc pre umiestnenie okna do stredu obrazovky
center_x = int((screen_width - window_width) / 2)
center_y = int((screen_height - window_height) / 2)

# Umiestnenie okna do stredu obrazovky
app.geometry(f"+{center_x}+{center_y}")

app.title("Amp Sender") 
app.mainloop() 