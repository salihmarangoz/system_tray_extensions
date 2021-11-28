#!/bin/bash

sudo add-apt-repository universe

sudo apt-get install -y \
  libgirepository1.0-dev \
  libcairo2-dev \
  pkg-config \
  python3-dev \
  build-essential \
  libdbus-1-dev \
  libxcb-xinerama0 \
  gir1.2-appindicator3-0.1