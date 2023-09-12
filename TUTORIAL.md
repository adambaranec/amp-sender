## How to use
- When starting the app, choose an input from the list to record from (e.g. microphone).
- If you would like to record everything which sounds from your device, make necessary sound connections (for example in Linux) or simply configure a virtual audio cable. Then, choose the virtual cable as the input in Amp Sender.

## Using Amp Sender with Hydra (overall JavaScript)
Hydra itself is able to capture sound, but only from the default built-in microphone. In case of a custom device, read further.

- In Amp Sender, set the WebSocket connection type and port to 8080.
- Copy this code to the Hydra editor:
```
await loadScript("https://cdn.jsdelivr.net/gh/ojack/hydra-osc/lib/osc.min.js")

_osc = new OSC()
_osc.open()

amp = 0
_osc.on('/amp', (m)=>{amp = m.args[0]})
```
The OSC receiver will open at port 8080. To make a parameter changeable throughout time, use arrow function for it.

Example:
```
shape(100).scale(()=>amp).out()
```
## Custom connection (e.g. Processing, Python, openFrameworks etc.)
Make sure the programming language (or environment, software) you set up visualizations in provides libraries or support for OSC (Open Sound Control). Implement a way to listen to incoming messages from Amp Sender on the address '/amp' - depends on the library you use.
## Sending volume to other devices
Before setting things up:
- All devices to send messages including yours must be connected to the same network
- Find the public IP address of your device (in its settings)
- The IP address should serve as the host to set in Amp Sender
- All receivers should then try to connect to the same host and port defined in the app
