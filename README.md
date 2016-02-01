# QR SCANNER for Arrow v2 #

###### Notes ######
1. Reads only QR codes
2. Configuration is in `src/config.ini`, docker image `/root/qr-scanner/config.ini`

###### Requirements ######
- Python (2.7)
- libav 9 (Ubuntu 14.04 repo)
- libzbar-dev (Ubuntu 14.04 repo)
- avpy (pip)
- zbar (pip)
- Pillow (pip)

###### Run ######
1. `python qr-scanner streamAddress [timeout_in_seconds] [writeDebug]`

Parameter          | Description
------------------ | -------------
timeout_in_seconds | Length of run of program. Connection time is included. If ommited, default value will be used (1 minute)
writeDebug         | Will set debug logging level and will write logs to stdout, must be second parameter

###### Run in docker ######
`docker run angelcam/arrow-qr-scanner:latest http://e2-eu1.angelcam.com/m2-eu1/10807/playlist-cra.m3u8 60`

- debug version:

`docker run angelcam/arrow-qr-scanner:latest http://e2-eu1.angelcam.com/m2-eu1/10807/playlist-cra.m3u8 60 writeDebug`


###### Behavior notes ######
- program will run whole timeout_in_seconds and write all detected QR codes
- every detected code is written only once

###### Outputs ######
1. In case of success:
    1. decoded QR codes, one per line
    2. stdout will contain "Timeout." after end of program
2. In case of error:
    1. decoded QR codes, one per line
    2. stderr will contain "Timeout. XXX", where XXX is error message


###### Error messages ######
Error                                                    | Description
---------------------------------------------------------| -------------
Timeout. Could not connect to stream (demuxing problem). | scanner couldn't connect to stream | posssible cause: bad address, totally broken stream
Timeout. Could not read or decode packets (corrupted stream). | scanner connected to stream, but couldn't decode even one frame | broken stream, no keyframes
Timeout. Could not find or decode qr code (code not in stream). | scanner decoded some frames from stream, but couldn't find QR code in them | QR code is too far from camera, too small, bent, blurry, out of camera field of view or bad lightning conditions
main: description of problem with arguments | scanner cannot parse input parameters
