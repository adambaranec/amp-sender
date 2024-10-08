## How to use
- When starting the app, choose an input from the list to record from (e.g. built-in microphone).
- Set a host and a port to send messages.
- Tip 1: If you would like to record sounds coming from your device (e.g. background music from Spotify), make necessary sound connections (for example with JACK in Linux) or simply configure a multi-output with a virtual audio cable (BlackHole 16ch etc.). Then, choose the cable as the input in Amp Sender.
- Tip 2: The host is by default set to localhost (127.0.0.1) - the amplitude of current sounds is sent to an OSC receiver in the same computer. If such receiver is running in another computer, host has to be set as the IP address of the sender (computer where Amp Sender is running).

![app screenshot](screenshot.png)

## Using Amp Sender with Hydra (overall JavaScript)
Hydra itself is able to capture sound, but only from the default built-in microphone. Before using another device, read more.

- In Amp Sender, set your desired device to record from, the WebSocket connection type and port to 8080 (as creating an empty WebSocket in JS sets its port to 8080). Then click "Start sending".
- Copy and run this code in the Hydra editor:

```
await loadScript("https://cdn.jsdelivr.net/gh/ojack/hydra-osc/lib/osc.min.js")

_osc = new OSC()
_osc.open()

amp = 0
_osc.on('/amp', (m)=>{amp = m.args[0]})
```
The OSC receiver will open at port 8080. To make the parameter every frame updated, declare it in arrow functions - not just ```amp```.

Examples:
```
shape(100).scale(()=>amp).out()

solid(1,()=>amp*.5,0).out()
```

## Sending volume to other devices
Before setting things up:
- All devices acting as OSC receivers including yours must be connected to the same network
- Find the public IP address of your device (in its settings, do not search it with Google)
- The IP address should serve as the host to set in Amp Sender
- All receivers should then try to connect to the same host and port defined in the app
