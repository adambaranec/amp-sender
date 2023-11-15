# © Adam Baranec, 2023

import sounddevice as sd 

import numpy as np 

import asyncio

import websockets as ws

import threading 

import tkinter as tk

from tkinter import ttk

import pythonosc as pyosc

from pythonosc import udp_client

from pythonosc.dispatcher import Dispatcher

from pythonosc import osc_server

from pythonosc import osc_message_builder

from pythonosc import osc_bundle_builder

import json

import time

is_sending = False
udp_running = False
ws_running = False

app = tk.Tk()

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

FPS = 60
MODE = 'UDP'

def devices():
  devs = sd.query_devices()
  names = []
  for device in devs: 
    names.append(device.get('name'))
  return names

HOST = tk.StringVar() 
PORT = tk.StringVar()

ipOutLabel = tk.Label(text="IP (Outcoming)") 

ipOut = tk.Entry(textvariable=HOST) 
ipOut.insert(tk.END,'127.0.0.1')

portOutLabel = tk.Label(text="Port (Outcoming)") 

portOut = tk.Entry(textvariable=PORT) 


chosen_device = tk.StringVar()

devicesList = tk.ttk.Combobox(app, values=devices(), textvariable=chosen_device, state="readonly")
devicesList.set(devices()[0])

status = tk.Text(app, height=3, width=60, bg='gray')
status.tag_configure("center", justify='center')

server_type = tk.StringVar()
server_type_settings = tk.ttk.Combobox(app, values=['UDP', 'WebSocket'], state="readonly", textvariable=server_type, width=9, justify="center")
server_type_settings.set('UDP')

create_server = tk.BooleanVar()
create_server.set(False)
create_server_checkbox = tk.Checkbutton(app, text="Create internal server", variable=create_server)

def start():
   global MODE
   global is_sending
   global udp_running
   global ws_running
   MODE = server_type.get()
   if PORT.get() != '': 
    try:
     is_sending = True
     #dispatcher = Dispatcher()
     match MODE:
      case 'UDP':
       client_udp = udp_client.SimpleUDPClient(HOST.get(), int(PORT.get()))
       udp_send(chosen_device.get(),client_udp)
       '''if create_server.get() == True:
        udp_running = True
        server_udp = osc_server.ThreadingOSCUDPServer((HOST.get(), int(PORT.get())), dispatcher)
        serve(server_udp)'''
      case 'WebSocket': 
       ws_running = True
       init_ws()
       '''
       if create_server.get() == True:
         server_udp = osc_server.ThreadingOSCUDPServer((HOST.get(), int(PORT.get())-1), dispatcher)
         serve(server_udp)
         ws_thread = threading.Thread(target=init_ws)
         ws_thread.start()'''
     status.delete('1.0', tk.END)
     status.insert(tk.END, f"Sending to {MODE} {HOST.get()} and port {PORT.get()}", "center")
     status.pack()
    except Exception as e:
     status.delete('1.0', tk.END)
     status.insert(tk.END, e, "center")
     status.pack() 
   else:
    status.delete('1.0', tk.END)
    status.insert(tk.END, "Cannot send amplitude without port\n", "center")
    status.pack() 
  
'''def serve(server):
  if isinstance(server, osc_server.ThreadingOSCUDPServer):
   global udp_running
   if udp_running == True: 
    threading.Thread(target=server.serve_forever).start()
   else:
    server.server_close()'''

def init_ws():
 async def handler(websocket, path):
  ip, port = websocket.remote_address
  status.insert(tk.END, f"\nClient connected from {ip} and port {port}", "center")
  try:
   await ws_send(chosen_device.get(),websocket)
  except Exception as e:
   status.delete('1.0', tk.END)
   status.insert(tk.END, f"Server log: {e}", "center")

 global is_sending
 is_sending = True
 start_server = ws.serve(handler, HOST.get(), int(PORT.get()))
 asyncio.get_event_loop().run_until_complete(start_server)
 threading.Thread(target=asyncio.get_event_loop().run_forever).start()  

def udp_send(input_device,client):
  global FPS
  global MODE
  global is_sending
  if is_sending == True:
   sample = sd.rec(1, 44100, 1, np.float32, device=input_device)
   amp = sample[0][0]
   match MODE:
    case 'UDP':
     try:
      client.send_message("/amp", float(amp))
     except Exception as e:
      status.delete('1.0', tk.END)
      status.insert(tk.END, f"Client log: {e}", "center")
  time.sleep(1/FPS)
  udp_send(input_device,client)

async def ws_send(input_device,client):
  global FPS
  global MODE
  global is_sending
  if is_sending == True:
   sample = sd.rec(1, 44100, 1, np.float32, device=input_device)
   amp = sample[0][0]
   match MODE:
    case 'UDP':
     client.send_message("/amp", float(amp))
    case 'WebSocket':
     try:
      msg = osc_message_builder.OscMessageBuilder(address = "/amp")
      msg.add_arg(float(amp))
      msg = msg.build()
      bytes = msg.dgram
      await client.send(bytes)
     except Exception as e:
      status.delete('1.0', tk.END)
      status.insert(tk.END, f"Client log: {e}", "center") 
  time.sleep(1/FPS)
  await ws_send(input_device,client)

def close():
  global is_sending
  global udp_running
  global ws_running
  is_sending = False
  udp_running = False
  ws_running = False
  app.destroy()  

app.protocol("WM_DELETE_WINDOW", close)
    

start_button = tk.Button(app, text="Start sending", command=start)

fps = tk.StringVar()

def set_fps(*args):
  global FPS
  if fps.get() != '' and int(fps.get()) > 9:
   FPS = int(fps.get())

fps.trace("w", set_fps)
fps_label = tk.Label(text="FPS")
fps_settings = tk.Entry(app, textvariable=fps, width=4, justify="center")
fps_settings.insert(tk.END,'60')

devicesList.pack()
ipOutLabel.pack()
ipOut.pack()
portOutLabel.pack()
portOut.pack()
start_button.pack()
fps_label.pack()
fps_settings.pack()
server_type_settings.pack()
app.mainloop() 

