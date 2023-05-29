# [STE] System Tray Extensions

**Table of Contents**

- [Introduction](#introduction)
- [Supported Systems](#supported-systems)
- [Installation](#installation)
- [Running](#running)
- [Contributing](#contributing)
- [FAQ](#faq)
- [Known Issues and Solutions](#known-issues-and-solutions)
- [Credits](#credits)
- [References](#references)

## Introduction

STE is a RGB keyboard visualizer package for Tuxedo laptops. This package also provides a playground for playing with keyboard lights for tinkerers.


**Screenshot of the system tray application:**

![screenshot](.etc/screenshot.png)

**GIF: RGB Keyboard running `rgb_kb_custom/sin_wave.py`:**

![custom_py_script_ani](.etc/custom_py_script_ani.gif)

**GIF: RGB Keyboard running `rgb_kb_custom/cpu_usage.py` While Compiling a Project**

![custom_py_script.ani2](.etc/custom_py_script.ani2.gif)

**YOUTUBE: RGB Keyboard running `rgb_kb_custom/reflect_screen.py`:**

[![](https://img.youtube.com/vi/3v0SmxLNwq4/maxresdefault.jpg)](https://youtu.be/3v0SmxLNwq4)

**YOUTUBE: RGB Keyboard running various effects:**

[![](https://img.youtube.com/vi/3oub-UnJ8b8/maxresdefault.jpg)](https://youtu.be/3oub-UnJ8b8)

Also here are some other videos for RGB keyboard good for demonstration. Enable `rgb_kb_custom/reflect_screen.py` effect and watch the video in full-screen: [[1]](https://www.youtube.com/watch?v=2VsZTW6UjcA) [[2]](https://www.youtube.com/watch?v=2VsZTW6UjcA) [[3]](https://www.youtube.com/watch?v=5gT3migqxNI)

## Supported Systems

**Supported Distributions:**

- [![build-checks-debian](https://github.com/salihmarangoz/system_tray_extensions/actions/workflows/build_checks_debian.yml/badge.svg)](https://github.com/salihmarangoz/system_tray_extensions/actions/workflows/build_checks_debian.yml)
- [![build-checks-arch](https://github.com/salihmarangoz/system_tray_extensions/actions/workflows/build_checks_arch.yml/badge.svg)](https://github.com/salihmarangoz/system_tray_extensions/actions/workflows/build_checks_arch.yml)
- [![build-checks-debian](https://github.com/salihmarangoz/system_tray_extensions/actions/workflows/build_checks_fedora.yml/badge.svg)](https://github.com/salihmarangoz/system_tray_extensions/actions/workflows/build_checks_fedora.yml)

**Tested Systems:**

- Tuxedo Stellaris 15 Gen 3 - Ubuntu 20.04
- Tuxedo Stellaris 15 Gen 3 - Manjaro 21.1.6
- XMG Fusion 15 / Eluktronics MAG-15 - PopOS! 20.04, ElementaryOS 6, Nobara 37

## Installation

Start a new terminal session and use it for all commands above. If you want to run these in multiple terminals don't forget to define `INSTALL_DIR`.

```bash
# Specify installation directory
$ INSTALL_DIR="$HOME/.system_tray_extensions"

# Download the project
$ git clone https://github.com/salihmarangoz/system_tray_extensions.git "$INSTALL_DIR"
$ cd $INSTALL_DIR

# ONLY RUN ONE OF THESE ACCORDING TO YOUR LINUX DISTRIBUTION:
$ bash install_debian.sh # For Debian based distributions; Ubuntu, Pop OS, etc.
$ bash install_arch.sh # For Arch based distributions; Manjaro, etc. 
$ bash install_fedora.sh # For Fedora based distributions
```

- Create a file `/etc/udev/rules.d/99-ste.rules` for device permissions and copy/paste the following:

```bash
# RGB Keyboard
SUBSYSTEMS=="usb", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="6004", MODE:="0666"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="ce00", MODE:="0666"

# Optional: Lightbar (Tuxedo Keyboard)
# Controlling lightbar using the interface provided by tuxedo-keyboard.
# Install the required package and uncomment TuxedoKeyboard line in modules/loading_order.list
SUBSYSTEM=="leds", ACTION=="add", RUN+="/bin/chgrp -R leds /sys%p", RUN+="/bin/chmod -R g=u /sys%p"
SUBSYSTEM=="leds", ACTION=="change", ENV{TRIGGER}!="none", RUN+="/bin/chgrp -R leds /sys%p", RUN+="/bin/chmod -R g=u /sys%p"
```

- After creating the file run:

```bash
# Optional: For controlling the Lightbar (Tuxedo Keyboard)
# Create `leds` group and add current user to it. 
$ sudo groupadd leds
$ sudo usermod -a -G leds $USER
```

- And lastly reboot the system. If you don't want to reboot; logout and login, then run `sudo udevadm control --reload`, then run `sudo udevadm trigger`. 

## Running

You can start the app via launcher. Also, the app will start on boot by default. 

If you want to start via terminal (maybe for debugging) then run this command:

```bash
$ bash start.sh
```



## Contributing

Contributions of any kind are welcome. See **ToDo List** for current problems/ideas.

**Contributors:**

- **[Invertisment](https://github.com/Invertisment)**
- **[augustoicaro](https://github.com/augustoicaro)**

**ToDo List:**

- [ ] Core: Check hibernate/wakeup if it works.
- [ ] RgbKeyboard: Keyboard shortcuts for effects? "Save this state to shortcut: xyz"?
- [ ] TogglePulseaudioSuspend
- [ ] App: Logging has some problems. Not working?!
- [ ] Add a check if battery path exists!
- [ ] Add a check if lightbar path exists!



## FAQ

- There are tons of dependencies, GTK, system tray thing but I don't want them.
  - Solution: Check this lightweight fork: https://gitlab.com/Ranguna/tuxedo-rgb-keyboard-daemon
- What happened to `ite8291r3-gui` ? 
  - It was only for ite8291r3 so I refactored the whole project. If you want then get it here: https://github.com/salihmarangoz/ite8291r3-gui/tree/ite8291r3-gui

## Known Issues and Solutions

- `tdp` package is causing rgb keyboard animations to stop.
  - Solution: Uninstall `tdp`. If you know how to prevent tdp from modifying USB power I welcome pull  requests.
- Other icons are not shown properly in XFCE. (If someone knows how please send a pull request)
- Pacman fails with 404:
  - Solution: https://github.com/salihmarangoz/system_tray_extensions/pull/39#pullrequestreview-803832786
- Can't install on Arch:
  - Solution `pacman -Sy` and then `pacman -S sudo` . Didn't work? Open an issue please.
- System tray submenus don't work on elementaryOS 6: (Solution by **[augustoicaro](https://github.com/augustoicaro)**):
  - https://elementaryos.stackexchange.com/questions/17452/how-to-display-system-tray-icons-in-elementary-os-juno#comment28965_17453



## Credits

Credit goes to [Ambiefix](https://www.youtube.com/channel/UCnwLT9GEwbzfjPusVKtxacA) for preset videos used in the RGB Keyboard module:

- [Youtube: Aurora Borealis Inspired Ambient Animation Video Backdrop Loop (60 min/No sound) - Free Footage](https://www.youtube.com/watch?v=X6PLRiil2F4)
- [Youtube: Rotating Colorful Waves - Rainbow Lines - Motion Graphics Video Background](https://www.youtube.com/watch?v=sTsO_NMjb3o)
- [Youtube: Blurred Lines Spaghetti Ambient Mood Light Video Loop (2 Hours/No Sound)](https://www.youtube.com/watch?v=Nw9vgfbPf90)

Credit goes to [MrPacMan36](https://www.youtube.com/channel/UC7GfgbTJuA6_gi2XEaBcNRw) for the video used in the RGB Keyboard demo video:

- [Youtube: Fluid Sim Hue Test](https://www.youtube.com/watch?v=qC0vDKVPCrw)



## References

- https://approxeng.github.io/approxeng.input/sys.html
