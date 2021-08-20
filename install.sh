#!/bin/bash

INSTALL_DIR="$HOME/.local/share/ite8291r3_gui"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"


echo "[*] Installing Python3 Dependencies"
pip install ite8291r3-ctl PyQt5 pyusb


echo "[*] Creating udev rules for ite8291"
sudo tee /etc/udev/rules.d/99-ite8291.rules << END
SUBSYSTEMS=="usb", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="ce00", MODE:="0666"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="6004", MODE:="0666"
END


echo "[*] Installing the app into $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/app/ite_tray.py" "$INSTALL_DIR/ite_tray.py"
cp "$SCRIPT_DIR/app/icon.png" "$INSTALL_DIR/icon.png"


echo "[*] Creating/overwriting autostart entry"
tee $HOME/.config/autostart/ite8291r3_gui.desktop << END
[Desktop Entry]
Type=Application
Exec=/usr/bin/python3 $INSTALL_DIR/ite_tray.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[en_US]=ite8291r3-gui
Name=ite8291r3-gui
Comment[en_US]=
Comment=
END

echo "[*] Done!"