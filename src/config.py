#Configuraiton file

#default job timeout length
TIMEOUT_S = 60


# number of frames to skip
SKIP_FRAMES = 10

# Streamreader
# image packet queue size - HLS input, packets downloaded at start = 40s * 25frames = 1000
MAX_PACKETS = 100

# timeout for connecting to stream = downloading first few packets to analyse stream
DEMUXER_TIMEOUT_OPEN_INPUT = 30

# demuxer reading timeout length (number) [s]
DEMUXER_TIMEOUT_READ_FRAME = 10
