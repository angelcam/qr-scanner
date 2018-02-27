import logging

# default minimal log level
LOG_LEVEL = logging.INFO

# default job timeout length
TIMEOUT_S = 60

# timeout for connecting to stream = downloading first few packets to analyse stream
DEMUXER_TIMEOUT_OPEN_INPUT = 30

# demuxer reading timeout length (number) [s]
DEMUXER_TIMEOUT_READ_FRAME = 10

# Streamreader
# image packet queue size - HLS input, packets downloaded at start = 40s * 25frames = 1000
MAX_PACKETS = 200

# maximal length of widht or height of input image
# large image is scaled to x:DECODER_MAX_RESOLUTION or DECODER_MAX_RESOLUTION:y
# aspect ration is preserved
# 1000 is safe, 500 can work (number) [px]
DECODER_MAX_RESOLUTION = 1000

# Time between scanned images (number) [s]
# If scanning is too slow (time_of_scanning > SKIP_TIME), program will skip time_of_scanning
SKIP_TIME_S = 0.5
