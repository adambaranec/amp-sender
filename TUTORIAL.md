## Tips
- If you would like to capture everything what sounds through speakers, install a virtual audio cable and configure it.
- To try these connections, in Amp Sender disable the checkbox "Create internal server".

## Using Amp Sender with Hydra (overall JavaScript)
Hydra itself is able to capture sound, but only from the default built-in microphone. In case of a custom device, read further.

- In the app, set port to 8080.
- Copy this code to the Hydra editor:
```
await loadScript("https://cdn.jsdelivr.net/npm/osc-js@2.4.0/lib/osc.min.js")

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
## Custom connection
Make sure the programming language (or environment) you set up the visualizer in provides libraries or support for OSC (Open Sound Control). Implement a way to listen to incoming messages from Amp Sender - depends on the library you use.
## Sending volume to other devices
Before setting things up:
- All devices to send messages including yours must be connected to the same network
- Find the public IP address of your device (in its settings)
- The IP address should serve as the host to set in Amp Sender
- All receivers should then try to connect to the same host and port defined in the app
