# Dockerfile for qr-scanner

#take clean ubuntu - 64bit is default
FROM ubuntu:14.04

MAINTAINER Martin Dobrovolny <martin@angelcam.com>

#install necessary libraries
RUN apt-get update \
 && apt-get install -y python python-dev python-pip libavformat-dev libavcodec-dev  libavdevice-dev libavutil-dev libswscale-dev  libavresample-dev libavcodec-extra libzbar-dev \
 && pip install Avpy \
 && pip install zbar

#install av9.py actualization and qr-scanner
RUN mkdir /root/tmp/
ADD . /root/tmp/qr-scanner/
RUN cp /root/tmp/qr-scanner/src/avpy/av9.py /usr/local/lib/python2.7/dist-packages/avpy/version/ \
 && mkdir /root/qr-scanner \
 && cp /root/tmp/qr-scanner/src/*.py /root/qr-scanner/

#run command
WORKDIR /root/qr-scanner
ENTRYPOINT ["python", "-u", "qr-scanner.py"]

