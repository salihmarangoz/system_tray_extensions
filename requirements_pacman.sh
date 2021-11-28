#!/bin/bash
# Source: https://github.com/gfduszynski/cm-rgb/issues/45#issuecomment-920936950
sudo pacman -S $PACMAN_EXTRA_ARGS \
  cairo \
  gobject-introspection \
  pkgconf \
  gtk3 \
  pkg-config \
  base-devel \
  xdg-utils \
  libappindicator-gtk3
