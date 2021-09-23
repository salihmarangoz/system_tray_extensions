# [STE] System Tray Extensions

Description todo



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

Do you have a good idea? Would you like to send a pull request? See [CONTRIBUTING.md](CONTRIBUTING.md)





## To-Do

- Track hibernate/suspend and battery plugged/unplugged actions and send them as events
- Better gamma correction. (I don't have any device to calibrate it. Also this is not a solution. But better estimations would be nice.)
- Report brightness in the menu. And put "+" and "-" into the same entry.
- pip3 install to virtual environment?
- Keyboard shortcuts for effects? "Save this state to shortcut: xyz"
- Sound spectrum analyzer
- Forwards logs to journalctl or to a file?
- low battery alert with ite drivers

**Rework Path:**

- Install will be done via `git clone` and `bash install.sh`, update will be done via `git pull` 
- https://askubuntu.com/questions/308067/how-to-run-a-script-after-or-before-hibernate

 
