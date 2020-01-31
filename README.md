# QR code scanner

The library is just a thin wrapper over the Rust `qr_scanner`. It allows
scanning QR codes from video streams delivered via HTTP(S). Please note
that the whole stream must be encapsulated within one HTTP response body.
Video streams delivered in multiple HTTP responses (such as HLS) won't work
with the scanner.

## Installation

The wrapper expect `libqr_scanner.so` to be present in the system. You
can get it by building the corresponding Rust library and installing it
into the system.

## Usage

```python
import qr_scanner

for code in qr_scanner.scan('https://my.domain/video.mp4', 20):
    print(code.decode('utf-8'))
```
