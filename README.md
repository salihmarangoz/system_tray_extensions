# [STE] System Tray Extensions



## Extensions

- [ite8291r3-ctl](https://github.com/pobrn/ite8291r3-ctl) (RGB Keyboard Driver for `048d:6004` and `048d:ce00`)
- Lightbar Controller (e.g. [Tuxedo laptops](https://www.tuxedocomputers.com/en/Infos/Help-Support/Instructions/Installation-of-keyboard-drivers-for-TUXEDO-Computers-models-with-RGB-keyboard-.tuxedo))
- Touchpad Toggle On/Off
- dGPU Powerstate Monitor (for laptops)
- Battery Power Draw Monitor (for laptops)



## Running

App will start on boot by default. You can start it just after the installation with this command:

**TODO**

```bash
$ nohup python3 $HOME/.local/share/ite8291r3_gui/ite_tray.py # then close the terminal
```



## To-Do

- Track hibernate/suspend and battery plugged/unplugged actions and send them as events

- Better gamma correction. (I don't have any device to calibrate it. Also this is not a solution. But better estimations would be nice.)
- Report brightness in the menu. And put "+" and "-" into the same entry.
- pip3 install to virtual environment?
- Keyboard shortcuts for effects? "Save this state to shortcut: xyz"
- Sound spectrum analyzer
- Forwards logs to journalctl or to a file.

**Rework Path:**

- Install will be done via `git clone` and `bash install.sh`, update will be done via `git pull` 
- https://askubuntu.com/questions/308067/how-to-run-a-script-after-or-before-hibernate

 
