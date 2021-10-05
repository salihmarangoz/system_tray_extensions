# For ite8291r3-gui check the other branch

Old package is here: https://github.com/salihmarangoz/ite8291r3-gui/tree/ite8291r3-gui

The new app (STE) will include ite8291r3 as an extension with many features. Also, lightbar control, custom scripts, and many things will be available. Custom modules will be able to to access useful events (lid opened, lid closed, before suspend, after suspend, ac adapter plugged in, battery mode, etc.) without effort.



# [STE] System Tray Extensions

Currently under development. Don't pay attention to the docs!

Currently under development. Don't pay attention to the docs!

Currently under development. Don't pay attention to the docs!

Currently under development. Don't pay attention to the docs!



## Demos

### RGB Keyboard Driver

[![](https://img.youtube.com/vi/3v0SmxLNwq4/maxresdefault.jpg)](https://youtu.be/3v0SmxLNwq4)



## Modules

| Ready? | Name (click for readme)                                      | Description                                                  |
| ------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| No     | [Ite8291r3Ctl](modules/Ite8291r3Ctl/README.md)               | [ite8291r3-ctl](https://github.com/pobrn/ite8291r3-ctl) RGB Keyboard Driver for `048d:6004` and `048d:ce00` |
| No     | [LightbarHid](modules/LightbarHid/README.md)                 | Lightbar controller for TongFang based laptops (e.g. [Tuxedo](https://www.tuxedocomputers.com/en/Infos/Help-Support/Instructions/Installation-of-keyboard-drivers-for-TUXEDO-Computers-models-with-RGB-keyboard-.tuxedo), XMG, Eluktronics) |
| No     | [TouchpadToggle](modules/TouchpadToggle/README.md)           | Enable/disable touchpad device with `xinput`                 |
| No     | [DgpuPowerstateMonitor](modules/DgpuPowerstateMonitor/README.md) | Adds a system tray icon indicating dGPU is active. Can be activated only in battery mode. |
| No     | [BatteryPowerDrawMonitor](modules/BatteryPowerDrawMonitor/README.md) | Adds a system tray icon indicating power drawn from the battery. Can be activated only in battery mode. |
| No     | [TogglePulseaudioSuspend](modules/TogglePulseaudioSuspend/README.md) | Adds/removes [`module-suspend-on-idle`](https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/Modules/#module-suspend-on-idle) depending on if the device is in laptop or AC mode. |
| No     | CheckUpdates                                                 | todo                                                         |



## Installation/Update

todo



## Running

App will start on boot by default. You can start it just after the installation with this command:

```bash
$ nohup python3 $HOME/.local/share/ite8291r3_gui/ite_tray.py # then close the terminal
```



## Contributing

Contributions of any kind are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md)



## Credits

Credit goes to [Ambiefix](https://www.youtube.com/channel/UCnwLT9GEwbzfjPusVKtxacA) for preset videos used in the RGB Keyboard module:

- [Youtube: Aurora Borealis Inspired Ambient Animation Video Backdrop Loop (60 min/No sound) - Free Footage](https://www.youtube.com/watch?v=X6PLRiil2F4)
- [Youtube: Rotating Colorful Waves - Rainbow Lines - Motion Graphics Video Background](https://www.youtube.com/watch?v=sTsO_NMjb3o)

Credit goes to [MrPacMan36](https://www.youtube.com/channel/UC7GfgbTJuA6_gi2XEaBcNRw) for the video used in the RGB Keyboard demo video:

- [Youtube: Fluid Sim Hue Test](https://www.youtube.com/watch?v=qC0vDKVPCrw)



------------------------------



## Core ToDo's

- Add callback in an anonymous way



## To-Do

- Track hibernate/suspend and battery plugged/unplugged actions and send them as events
- Report brightness in the menu. And put "+" and "-" into the same entry.
- pip3 install to virtual environment?
- Keyboard shortcuts for effects? "Save this state to shortcut: xyz"
- Forwards logs to journalctl or to a file?
- low battery alert with ite drivers

**Rework Path:**

- Install will be done via `git clone` and `bash install.sh`, update will be done via `git pull` 
- https://askubuntu.com/questions/308067/how-to-run-a-script-after-or-before-hibernate

 
