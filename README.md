# QR SCANNER for Arrow v2 #

###### Notes ######
1. Reads only QR codes
2. Configuration is in `src/config.py`, docker image `/root/qr-scanner/config.py`

###### Use ######
See hello_world in examples

###### Run for testing ######
1. `python3 hello_world.py [-h] [-t TIMEOUT] [-d] url
`

Parameter          | Description
------------------ | -------------
url         | stream url
-t TIMEOUT | Length of run of program. Connection time is included. If ommited, default value will be used (60 seconds)
-d         | Will set debug logging level and will write logs to stdout


###### Error messages ######
Error                                                    | Description
---------------------------------------------------------| -------------
Timeout. Could not connect to stream (demuxing problem). | scanner couldn't connect to stream | posssible cause: bad address, totally broken stream
Timeout. Could not read or decode packets (corrupted stream). | scanner connected to stream, but couldn't decode even one frame | broken stream, no keyframes
Timeout. Could not find or decode qr code (code not in stream). | scanner decoded some frames from stream, but couldn't find QR code in them | QR code is too far from camera, too small, bent, blurry, out of camera field of view or bad lightning conditions
main: description of problem with arguments | scanner cannot parse input parameters
