import sounddevice as sd 

import numpy as np 

import socket 

import threading 

import tkinter as tk

from tkinter import ttk

import pythonosc as pyosc

from pythonosc import udp_client

from pythonosc.dispatcher import Dispatcher

from pythonosc import osc_server

app = tk.Tk()

def close():
 app.destroy()

app.protocol("WM_DELETE_WINDOW", close)

# Získanie rozmerov obrazovky
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

window_width = int(screen_width / 4)
window_height = int(screen_height / 4)
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

status = tk.Text(app, height=1, width=window_width, bg='gray')
status.tag_configure("center", justify='center')

server_type = tk.StringVar()
server_type_settings = tk.ttk.Combobox(app, values=['UDP', 'WebSocket'], state="readonly", textvariable=server_type, width=int(window_width/80), justify="center")
server_type_settings.set('UDP')

create_server = tk.BooleanVar()
create_server.set(True)

create_server_checkbox = tk.Checkbutton(app, text="Create internal server", variable=create_server)


def start():
   global MODE
   MODE = server_type.get()
   if PORT.get() != '': 
    try:
     dispatcher = Dispatcher()
     match MODE:
      case 'UDP':
       client_udp = udp_client.SimpleUDPClient(HOST.get(), int(PORT.get()))
       send(chosen_device.get(),client_udp)
       if create_server.get() == True:
        server_udp = osc_server.ThreadingOSCUDPServer((HOST.get(), int(PORT.get())), dispatcher)  
        threading.Thread(target=server_udp.serve_forever).start()
      case 'WebSocket':
       threading.Thread(target=init_ws).start()
       # Just to differentiate between UDP and WebSocket ports are just subtracted by one
       client_udp = udp_client.SimpleUDPClient(HOST.get(), int(PORT.get())-1)
       server_udp = osc_server.ThreadingOSCUDPServer((HOST.get(), int(PORT.get())-1), dispatcher)
       dispatcher.map("/amp", ws_send)
       send(chosen_device.get(),client_udp)
       threading.Thread(target=server_udp.serve_forever).start()  
       if create_server.get() == True:
        threading.Thread(target=init_ws).start()
     status.delete('1.0', tk.END)
     status.insert(tk.END, f"Sending to {MODE} {HOST.get()} and port {PORT.get()}\n", "center")
     status.pack()
    except Exception as e:
     status.delete('1.0', tk.END)
     status.insert(tk.END, f"Exception: {e}", "center")
     status.pack() 
   else:
    status.delete('1.0', tk.END)
    status.insert(tk.END, "Cannot send amplitude without port\n", "center")
    status.pack() 

def init_ws():
    ws_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ws_server.bind((HOST.get(), int(PORT.get())))
    ws_server.listen()
    while True:
     client, addr = ws_server.accept()
     data = client.recv(2048)


def ws_send(addr,*args):
  import json
  message = {'address': addr, 'args': list(args)}
  ws = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  ws.connect((HOST.get(), int(PORT.get())))
  ws.sendall(json.dumps(message).encode('utf-8'))

def send(input_device,client):
  global FPS
  sample = sd.rec(1, 44100, 2, np.float32, device=input_device)
  amp = np.mean(sample[0])
  client.send_message("/amp", float(amp))
  threading.Timer(1/FPS, send, [input_device,client]).start()
    

start_button = tk.Button(app, text="Start", command=start)

stop_button = tk.Button(app, text="Stop")

fps = tk.StringVar()

def set_fps(*args):
  global FPS
  if fps.get() != '' and int(fps.get()) > 9:
   FPS = int(fps.get())

fps.trace("w", set_fps)
fps_label = tk.Label(text="FPS")
fps_settings = tk.Entry(app, textvariable=fps, width=int(window_width/120), justify="center")
fps_settings.insert(tk.END,'60')

devicesList.pack()
ipOutLabel.pack()
ipOut.pack()
portOutLabel.pack()
portOut.pack()
start_button.pack()
stop_button.pack()
fps_label.pack()
fps_settings.pack()
server_type_settings.pack()
create_server_checkbox.pack()
app.mainloop() 

