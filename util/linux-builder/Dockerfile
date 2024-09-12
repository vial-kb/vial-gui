FROM ubuntu:18.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y libusb-1.0-0-dev libudev-dev ruby ruby-dev rubygems build-essential desktop-file-utils wget unzip zlib1g-dev liblzma-dev libssl-dev git imagemagick file libfuse2

RUN wget https://github.com/AppImage/pkg2appimage/archive/38603d92359a48189c35debad9005e8e902e6070.zip && \
    unzip *.zip && \
    gem install dotenv -v 2.8.1 && \
    gem install --no-document fpm && \
    fpm --version

COPY . /vial-gui

RUN /vial-gui/util/setup_python36.sh
