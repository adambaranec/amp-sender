import sounddevice as sd 

import numpy as np 

import socket 

import threading 

import tkinter as tk

from tkinter import ttk

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

server_type = tk.StringVar()

types = ['UDP','TCP']

server_type_settings = tk.ttk.Combobox(app, textvariable=server_type, values=types, state='readonly', width=int(window_width/100))
server_type_settings.set('TCP')

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP as default

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

server_runs = False

def connect(host, port): 
        # UDP server
        """
        global server_runs
        global server
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind((host, int(port))) 
        status.delete('1.0', tk.END)
        status.insert(tk.END, "Server running on " + host + " and port " + str(port))
        status.configure(state=tk.DISABLED)
        status.pack()
        server_runs = True
        while server_runs:
            data, addr = server.recvfrom(1024)  
            if chosen_device.get() != "":
             send(server,chosen_device.get(),addr)
            else:
             status.configure(state=tk.NORMAL)
             status.insert(tk.END, "\nNo device chosen")
             status.configure(state=tk.DISABLED)"""
        # TCP server
        global server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with server as s: 
         s.bind((host, int(port))) 
         s.listen(0)
         status.delete('1.0', tk.END)
         status.insert(tk.END, "Server running on " + host + " and port " + str(port))
         status.configure(state=tk.DISABLED)
         status.pack()
         conn, addr = s.accept()
         with conn: 
          try:
           status.configure(state=tk.NORMAL)
           status.insert(tk.END, "\nClient connected from " + str(addr[0]) + " and port " + str(addr[1]))
           status.configure(state=tk.DISABLED)
           if chosen_device.get() != '':
            threading.Thread(target=send, args=(conn,chosen_device.get())).start()
           else:
            status.insert(tk.END, "\nNo device chosen")
          except ConnectionAbortedError:
             conn.close()
               

# send - UDP server
"""def send(server,device,addr): 
            global FPS
            audio = sd.rec(1, samplerate=44100, channels=2, dtype=np.float32,device=device) 
            sd.wait() 
            amplituda = np.mean(audio[0])
            server.sendto(str(amplituda).encode('utf-8'), addr)
            threading.Timer(float(1/FPS), send, args=(server,device,addr)).start()"""
# send - TCP server
def send(connection,device):
            global FPS
            audio = sd.rec(1, samplerate=44100, channels=2, dtype=np.float32,device=device) 
            sd.wait() 
            amplituda = np.mean(audio[0])
            connection.sendall(str(amplituda).encode('utf-8'))
            threading.Timer(float(1/FPS), send, args=(connection,device)).start()



def start_server(): 
    handler = threading.Thread(target=connect, args=(ipOut.get(),int(portOut.get())))
    handler.start()
    threading.Timer(10.0, lambda: handler.stop())

def stop_server(): 
    global server
    global server_runs
    server_runs = False
    server.close()
    status.delete('1.0', tk.END)
    status.pack_forget()
    

start_button = tk.Button(app, text="Start", command=start_server)

stop_button = tk.Button(app, text="Stop", command=stop_server)

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
server_type_settings.pack()
app.mainloop() 

"""def control(): 
 try:
    with socket.create_connection((ipOut.get(),int(portOut.get())), timeout=1):
        print("Server works")
 except socket.error:
       print("Does not work")
 threading.Timer(2, control).start()"""

