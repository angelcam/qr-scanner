README for qrScanner for Arrow v2.

Requirements:
Python (2.7)
libav 9 (Ubuntu 14.04 repo)
apt-get (Ubuntu 14.04 repo)
avpy (pip)
ZBar (pip)

Run:
python qr-scanner streamAddress [timeout_in_seconds] [logger_level]
timeout_in_seconds - if ommited, default value will be used (1 minute)
logger_level - debug, info, error, fatal - default value is info

TODO add input and output formats