# Announcement

Adding multiple functionality to this project was a bad idea. So I will crop functionalities other than RGB keyboard. And I will make this project be able to run in CLI. I haven't decided on a new name yet but I think it will be `ste-rgb-keyboard`. Other parts such as  `DgpuPowerstateMonitor` and `BatteryPowerDrawMonitor` will be published as a new small projects. Sorry for the inconvenience!

And I am thinking about publishing this project as a Flatpak, Snap and/or AppImage. So, installation and update will be easier.

# [STE] System Tray Extensions

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Supported Systems](#supported-systems)
- [Modules](#modules)
- [Installation](#installation)
- [Update](#update)
- [Running](#running)
- [Contributing](#contributing)
- [FAQ](#faq)
- [Known Issues and Solutions](#known-issues-and-solutions)
- [Credits](#credits)
- [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

System tray toolbox for Linux laptops. Currently includes tools for contolling keyboard and lightbar leds but new functions will be added in the future. Share your review here: https://github.com/salihmarangoz/system_tray_extensions/issues/19

**Screenshot of the system tray application:**

![screenshot](.etc/screenshot.png)

**YOUTUBE: RGB Keyboard running `rgb_kb_custom/reflect_screen.py`:**

[![](https://img.youtube.com/vi/3v0SmxLNwq4/maxresdefault.jpg)](https://youtu.be/3v0SmxLNwq4)

**GIF: RGB Keyboard running `rgb_kb_custom/sin_wave.py`:**

![custom_py_script_ani](.etc/custom_py_script_ani.gif)

**GIF: RGB Keyboard running `rgb_kb_custom/cpu_usage.py` While Compiling a Project**

![custom_py_script.ani2](.etc/custom_py_script.ani2.gif)

Also here are some other videos for RGB keyboard good for demonstration. Enable `rgb_kb_custom/reflect_screen.py` effect and watch the video in full-screen: [[1]](https://www.youtube.com/watch?v=2VsZTW6UjcA) [[2]](https://www.youtube.com/watch?v=2VsZTW6UjcA) [[3]](https://www.youtube.com/watch?v=5gT3migqxNI)

## Supported Systems

If there are modifications needed and woud like to share please send a pull request or write [HERE](https://github.com/salihmarangoz/system_tray_extensions/issues/19) so I can add them here too.

**Supported Distributions:**

- Debian: [![build-checks-debian](https://github.com/salihmarangoz/system_tray_extensions/actions/workflows/build_checks_debian.yml/badge.svg)](https://github.com/salihmarangoz/system_tray_extensions/actions/workflows/build_checks_debian.yml)
- Arch: [![build-checks-arch](https://github.com/salihmarangoz/system_tray_extensions/actions/workflows/build_checks_arch.yml/badge.svg)](https://github.com/salihmarangoz/system_tray_extensions/actions/workflows/build_checks_arch.yml)

**Tested Systems (Laptop/OS):**

- Tuxedo Stellaris 15 Gen 3 - Ubuntu 20.04
- Tuxedo Stellaris 15 Gen 3 - Manjaro 21.1.6
- XMG Fusion 15 - ???



## Modules

| Ready?            | Name (click for readme)                          | Description                                                  |
| ----------------- | ------------------------------------------------ | ------------------------------------------------------------ |
| Mostly            | [Core](modules/Core/README.md)                   | Handles process signals, dbus events, state & configuration files, GUI, etc. |
| Partially         | [UpdateManager](modules/UpdateManager/README.md) | Shows an entry in the STE menu (and optionally via notifications) if an update is available. Hidden otherwise. **Feedback is needed** |
| Mostly            | [Ite8291r3](modules/Ite8291r3/README.md)         | GUI for RGB keyboard led drivers that can control each LED separately. Currently only includes [ite8291r3-ctl](https://github.com/pobrn/ite8291r3-ctl) for `048d:6004` and `048d:ce00`. Can visualize custom .png, .mp4 and .py files. Also this module can be extended for new devices if there is a driver exists for it. |
| Only for LightBar | TuxedoKeyboard                                   | GUI for controlling [tuxedo-keyboard](https://github.com/tuxedocomputers/tuxedo-keyboard). Currently includes controls for Light-bar. See [this webpage](https://www.tuxedocomputers.com/en/Infos/Help-Support/Instructions/Installation-of-keyboard-drivers-for-TUXEDO-Computers-models-with-RGB-keyboard-.tuxedo) for more information. |
| Partially         | DgpuPowerstateMonitor                            | Adds an icon to system tray if dGPU is enabled. Only works or Nvidia for now. |
| Fully             | BatteryPowerDrawMonitor                          | Adds an icon to system tray showing power drawn from the battery. Hides itself on AC. The script can be run standalone. |
|                   | Script Manager                                   | todo                                                         |



## Installation

Start a new terminal session and use it for all commands above. If you want to run these in multiple terminals don't forget to define `INSTALL_DIR`.

```bash
# 0. Specify installation directory
$ INSTALL_DIR="$HOME/.system_tray_extensions"

# 1. Download the project
# Install git via apt or pacman before running the command below
$ git clone https://github.com/salihmarangoz/system_tray_extensions.git "$INSTALL_DIR"

# Next steps are included in the script (excluding permissions):
$ cd $INSTALL_DIR
# ONLY RUN ONE OF THESE ACCORDING TO YOUR LINUX DISTRIBUTION:
$ bash install_debian.sh # For Debian based distributions; Ubuntu, Pop OS, etc.
$ bash install_arch.sh # For Arch based distributions; Manjaro, etc. 
```

- Create a file `/etc/udev/rules.d/99-ste.rules` for device permissions and copy/paste the following:

```bash
# RGB Keyboard
SUBSYSTEMS=="usb", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="6004", MODE:="0666"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="ce00", MODE:="0666"

# Tuxedo Keyboard
SUBSYSTEM=="leds", ACTION=="add", RUN+="/bin/chgrp -R leds /sys%p", RUN+="/bin/chmod -R g=u /sys%p"
SUBSYSTEM=="leds", ACTION=="change", ENV{TRIGGER}!="none", RUN+="/bin/chgrp -R leds /sys%p", RUN+="/bin/chmod -R g=u /sys%p"
```

- after creating the file run:

```bash
# Create `leds` group and add current user to it. 
$ sudo groupadd leds
$ sudo usermod -a -G leds $USER
```

- and lastly reboot the system. If you don't want to reboot; logout and login, then run `sudo udevadm control --reload`, then run `sudo udevadm trigger`. 



## Update

Backup your installation before updating if you modified existing files. If you added new files it is OK. But, for example, if you modified some files (e.g. presets inside rgb_kb_custom) create a file named `.gitignore` and write `*` and place into that folder.

```bash
$ INSTALL_DIR="$HOME/.system_tray_extensions"
$ cd $INSTALL_DIR
$ git pull

# ONLY RUN ONE OF THESE ACCORDING TO YOUR LINUX DISTRIBUTION:
$ bash install_debian.sh # For Debian based distributions; Ubuntu, Pop OS, etc.
$ bash install_arch.sh # For Arch based distributions; Manjaro, etc. 

# Sometimes new devices can be added. Check the installation part if you waiting for a new device support!
```



## Running

You can start the app via launcher. Also, the app will start on boot by default. If you want to start via terminal then run this command:

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
