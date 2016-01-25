#Configuraiton file
import logger


# default minimal log level
LOG_LEVEL = logger.INFO

# default job timeout length
TIMEOUT_S = 60

# timeout for connecting to stream = downloading first few packets to analyse stream
DEMUXER_TIMEOUT_OPEN_INPUT = 30

# demuxer reading timeout length (number) [s]
DEMUXER_TIMEOUT_READ_FRAME = 10

# Streamreader
# image packet queue size - HLS input, packets downloaded at start = 40s * 25frames = 1000
MAX_PACKETS = 100

# Time between scanned images (number) [s]
# If scanning is too slow (time_of_scanning > SKIP_TIME), program will skip time_of_scanning
SKIP_TIME_S = 0.5

# number for dividing higher value of image width and height to get density
# density is how many line you skip in image evaluation (zbar uses 127x127)
# does not round e.g. 1920x1200 -> 1920/500 = 2 = every second row and column is used in scanning = (63x63 scan lines)
# 1000 is safe 500 works
SCAN_RES_DIVIDER = 500
