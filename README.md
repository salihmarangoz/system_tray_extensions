# For ite8291r3-gui check the other branch

Old package is here: https://github.com/salihmarangoz/ite8291r3-gui/tree/ite8291r3-gui

The new app (STE) will include ite8291r3 as an extension with many features. Also, lightbar control, custom scripts, and many things will be available. Custom modules will be able to to access useful events (lid opened, lid closed, before suspend, after suspend, ac adapter plugged in, battery mode, etc.) without effort.



# [STE] System Tray Extensions

todo: description



## Demos

### RGB Keyboard Driver

[![](https://img.youtube.com/vi/3v0SmxLNwq4/maxresdefault.jpg)](https://youtu.be/3v0SmxLNwq4)



## Modules

| Ready? | Name (click for readme)                                      | Description                                                  |
| ------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Yes    | [Core](modules/Core/README.md)                               | todo                                                         |
| Yes    | [RgbKeyboard](modules/RgbKeyboard/README.md)                 | Currently only includes [ite8291r3-ctl](https://github.com/pobrn/ite8291r3-ctl) for `048d:6004` and `048d:ce00`. Can be extended for new devices if there is a driver exists for it. |
| in dev | CheckUpdates                                                 | todo                                                         |
| No     | [LightbarHid](modules/LightbarHid/README.md)                 | Lightbar controller for TongFang based laptops (e.g. [Tuxedo](https://www.tuxedocomputers.com/en/Infos/Help-Support/Instructions/Installation-of-keyboard-drivers-for-TUXEDO-Computers-models-with-RGB-keyboard-.tuxedo), XMG, Eluktronics) |
| No     | [TouchpadToggle](modules/TouchpadToggle/README.md)           | Enable/disable touchpad device with `xinput`                 |
| No     | [DgpuPowerstateMonitor](modules/DgpuPowerstateMonitor/README.md) | Adds a system tray icon indicating dGPU is active. Can be activated only in battery mode. |
| No     | [BatteryPowerDrawMonitor](modules/BatteryPowerDrawMonitor/README.md) | Adds a system tray icon indicating power drawn from the battery. Can be activated only in battery mode. |
| No     | [TogglePulseaudioSuspend](modules/TogglePulseaudioSuspend/README.md) | Adds/removes [`module-suspend-on-idle`](https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/Modules/#module-suspend-on-idle) depending on if the device is in laptop or AC mode. |



## Installation

Start a new terminal session and use it for all commands above. If you want to run these in multiple terminals don't forget to define `INSTALL_DIR`.

```bash
# 0. Specify installation directory
$ INSTALL_DIR="$HOME/.system_tray_extensions"

# 1. Download the project
$ git clone https://github.com/salihmarangoz/system_tray_extensions.git "$INSTALL_DIR"
# OR
$ git clone git@github.com:salihmarangoz/system_tray_extensions.git "$INSTALL_DIR"

# 2. Create new virtual environment
# Note: I recommend using virtual environment to keep your pip installations clean
$ cd "$INSTALL_DIR"
$ python3 -m venv ste_env
$ echo "*" >> ste_env/.gitignore
$ source ste_env/bin/activate
$ pip3 install --upgrade pip
$ pip3 install wheel

# 3. Install dependencies
$ xargs sudo apt-get install < requirements_apt.txt
$ source ste_env/bin/activate
$ pip3 install -r requirements_pip.txt

# 4. Create desktop entry
# COPY THIS SECTION AND PASTE INTO TERMINAL
tee system_tray_extensions.desktop << END
[Desktop Entry]
Type=Application
Exec=$(which bash) $INSTALL_DIR/start.sh
Icon=$INSTALL_DIR/icon.png
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=System Tray Extensions
GenericName=STE
END
# UNTIL HERE

# 5. Add desktop entry to the Application Menu
$ xdg-desktop-menu install --novendor system_tray_extensions.desktop # Add the desktop entry to the apps menu

# 6. Enable application to run on Boot
$ cp system_tray_extensions.desktop $HOME/.config/autostart/
```



## Update

Backup your installation before updating if you modified existing files. If you added new files it is OK. But, for example, if you modified some files (e.g. presets inside rgb_kb_custom) create a file named `.gitignore` and write `*` and place into that folder.

```bash
$ cd $HOME/.system_tray_extensions
$ git pull
# Repeat installation steps 0, 3, 4, 5, 6
```



## Running

App will start on boot by default. You can start it just after the installation with this command:

```bash
$ bash start.sh
```



## Contributing

Contributions of any kind are welcome. See **ToDo List** for current problems/ideas. Also see [CONTRIBUTING.md](CONTRIBUTING.md)

**Contributors:**

- None

**ToDo List:**

- [ ] Core: Check hibernate/wakeup if it works.
- [ ] RgbKeyboard: Report brightness in the menu and modify brightness.
- [ ] RgbKeyboard: Keyboard shortcuts for effects? "Save this state to shortcut: xyz"?
- [ ] RgbKeyboard: low battery alert
- [ ] RgbKeyboard: Run screen mimic when screensaver starts on ac mode.
- [ ] Core: Add callback in an anonymous way
- [ ] *: Manage settings and module states.
- [ ] CheckUpdates: Show QtAction if update is available. Check every 6 hrs.
- [x] App: Add on boot entry for start.sh
- [x] App: Add desktop entry for start.sh
- [x] App: We need an ICON.
- [ ] App: Logging has some problems. Not working?!
- [ ] Import RgbKeyboard modules only when needed. (if another drivers are added)



## Credits

Credit goes to [Ambiefix](https://www.youtube.com/channel/UCnwLT9GEwbzfjPusVKtxacA) for preset videos used in the RGB Keyboard module:

- [Youtube: Aurora Borealis Inspired Ambient Animation Video Backdrop Loop (60 min/No sound) - Free Footage](https://www.youtube.com/watch?v=X6PLRiil2F4)
- [Youtube: Rotating Colorful Waves - Rainbow Lines - Motion Graphics Video Background](https://www.youtube.com/watch?v=sTsO_NMjb3o)

Credit goes to [MrPacMan36](https://www.youtube.com/channel/UC7GfgbTJuA6_gi2XEaBcNRw) for the video used in the RGB Keyboard demo video:

- [Youtube: Fluid Sim Hue Test](https://www.youtube.com/watch?v=qC0vDKVPCrw)
