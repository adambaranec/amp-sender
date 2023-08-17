import sounddevice as sd 

import numpy as np 

import socket 

import threading 

import tkinter as tk

from tkinter import ttk

server_bezi = False 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP

app = tk.Tk() 

app.geometry("100x100")


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

status = tk.Text(app, height=1, width=400)

def connect(host, port): 
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with server as s: 
        s.bind((host, int(port))) 
        s.listen() 
        status.delete('1.0', tk.END)
        status.insert(tk.END, "Server running on " + host + " and port " + str(port))
        status.pack()
        conn, addr = s.accept()
        server_bezi = True 
        with conn: 
          status.insert(tk.END, "\nClient connected with " + str(addr))
          if chosen_device.get() != '':
           threading.Thread(target=send, args=(conn,chosen_device)).start()
          else:
           status.insert(tk.END, "\nNo device chosen")   
        """while True:
            try:
                conn, addr = s.accept() 
                with conn: 
                 status.insert(tk.END, "\nClient connected with " + str(addr))
                 server_bezi = True 
                 threading.Thread(target=send, args=(conn,chosen_device)).start()
            except socket.error as e:
                status.delete('1.0', tk.END)
                status.insert(tk.END, e)"""

def send(connection,device): 
            while server_bezi: 
                audio = sd.rec(1, samplerate=44100, channels=2, dtype=np.float32,device=device) 
                sd.wait() 
                amplituda = audio[0]+1.0/2.0 
                connection.sendall(str(amplituda).encode('utf-8')) 
                threading.Timer(float(1/60), send, args=(connection,device)).start()
            

def start_server(): 
    threading.Thread(target=connect, args=(ipOut.get(),int(portOut.get()))).start()

def stop_server(): 
    global server_bezi 
    server_bezi = False 
    global server
    server.close()
    status.delete('1.0', tk.END)
    status.pack_forget()
    """try:
        server.shutdown(socket.SHUT_RDWR)
        server.close()
        status.delete('1.0', tk.END)
    except Exception as e:
         status.delete('1.0', tk.END)
         status.insert(tk.END, e)"""
    

start_button = tk.Button(app, text="Start", command=start_server)

stop_button = tk.Button(app, text="Stop", command=stop_server)

devicesList.pack()
ipOutLabel.pack()
ipOut.pack()
portOutLabel.pack()
portOut.pack()
start_button.pack()
stop_button.pack()
app.mainloop() 

"""def control(): 
 try:
    with socket.create_connection((ipOut.get(),int(portOut.get())), timeout=1):
        print("Server works")
 except socket.error:
       print("Does not work")
 threading.Timer(2, control).start()"""

