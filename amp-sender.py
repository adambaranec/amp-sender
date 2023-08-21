import sounddevice as sd 

import numpy as np 

import socket 

import threading 

import tkinter as tk

from tkinter import ttk

import pythonosc as pyosc

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

def devices():
  devs = sd.query_devices()
  names = []
  for device in devs: 
    names.append(device.get('name'))
  return names

ipOutLabel = tk.Label(text="IP (Outcoming)") 

ipOut = tk.Entry() 

portOutLabel = tk.Label(text="Port (Outcoming)") 

portOut = tk.Entry() 


chosen_device = tk.StringVar()

devicesList = tk.ttk.Combobox(app, values=devices(), textvariable=chosen_device, state="readonly")

status = tk.Text(app, height=1, width=window_width, bg='gray')
status.tag_configure("center", justify='center')

def send(device,host,port):
  amp = sd.rec(1,44100, 2, np.float32)
  amp.wait()
  pass
    

start_button = tk.Button(app, text="Start")

stop_button = tk.Button(app, text="Stop")

fps = tk.StringVar()

def set_fps(*args):
  global FPS
  if fps.get() != '' and int(fps.get()) > 9:
   FPS = fps.get()

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
app.mainloop() 

