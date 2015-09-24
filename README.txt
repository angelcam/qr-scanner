README for qrScanner for Arrow v2.

Requirements:
Python (2.7)
libav 9 (Ubuntu 14.04 repo)
libzbar-dev (Ubuntu 14.04 repo)
avpy (pip)
zbar (pip)

Run:
python qr-scanner streamAddress [timeout_in_seconds] [logger_level]
timeout_in_seconds - if ommited, default value will be used (1 minute)
logger_level - debug, info, error, fatal - default value is info. Or you can use value "writeDebug" to set level
    to debug nad write output to stdout

TODO:
- add input and output formats
- zbar supported code types