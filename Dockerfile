# Dockerfile for qr-scanner

# take clean ubuntu - 64bit is default
FROM ubuntu:16.04

MAINTAINER Martin Dobrovolny <martin@angelcam.com>

# install necessary libraries
RUN apt-get update \
 && apt-get install -y git python3 python3-pip python3-dev git wget build-essential yasm libx264-dev libzbar-dev openssl libssl-dev \
 && rm -rf /var/lib/apt/lists/*

# install ffmpeg and clean it (to make docker image smaller)
RUN wget http://ffmpeg.org/releases/ffmpeg-2.8.11.tar.xz \
 && tar -xf ffmpeg-2.8.11.tar.xz \
 && cd ffmpeg-2.8.11 \
 && ./configure --enable-libx264 --enable-gpl --enable-shared --disable-static --enable-openssl --enable-nonfree \
 && make \
 && make install \
 && ldconfig \
 && cd .. \
 && rm -rf ffmpeg*

# copy source repository
RUN mkdir /root/tmp/
ADD . /root/tmp/qr-scanner/

# install python requirements fix avpy ffmpeg detection and install ff28.py patch
RUN pip3 install --upgrade -r /root/tmp/qr-scanner/requirements.txt \
 && sed -i s/if\ libswresample\ and\ os\.path\.exists\(libswresample\):/if\ libswresample:/g /usr/local/lib/python3.5/dist-packages/avpy/av.py \
 && cp /root/tmp/qr-scanner/src/avpy/ff28.py /usr/local/lib/python3.5/dist-packages/avpy/version/

# install qr-scanner
RUN mkdir /root/qr-scanner \
 && cp /root/tmp/qr-scanner/src/*.py /root/qr-scanner/

# run command
WORKDIR /root/qr-scanner
ENTRYPOINT ["python3", "-u", "qr-scanner.py"]
