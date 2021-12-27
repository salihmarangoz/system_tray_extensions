#!/bin/bash
set -e
set -x

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

#INSTALL_DIR="$SCRIPT_DIR"
INSTALL_DIR=$(pwd)
#INSTALL_DIR="$HOME/.system_tray_extensions"

####################################################
echo "2. Create new virtual environment"
sudo apt install python3-venv
cd "$INSTALL_DIR"
python3 -m venv ste_env
echo "*" >> ste_env/.gitignore
source ste_env/bin/activate
pip3 install --upgrade pip
pip3 install wheel

####################################################
echo "3. Install dependencies"
cd "$INSTALL_DIR"
bash requirements_apt.sh
source ste_env/bin/activate
pip3 install -r requirements_pip.txt

####################################################
echo "4. Create desktop entry"
tee system_tray_extensions.desktop << END
[Desktop Entry]
Type=Application
Exec=$(which bash) $INSTALL_DIR/start.sh
Icon=$INSTALL_DIR/icon_full.png
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=System Tray Extensions
GenericName=STE
END

####################################################
echo "5. Add desktop entry to the Application Menu"
xdg-desktop-menu install --novendor system_tray_extensions.desktop

####################################################
echo "6. Enable application to run on Boot"
mkdir -p $HOME/.config/autostart/
cp system_tray_extensions.desktop $HOME/.config/autostart/