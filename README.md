# ite8291r3-gui

**Tested on Tuxedo Stellaris 15. Still in development!**

- Install dependencies

```
pip install ite8291r3-ctl PyQt5
```

- Copy the system tray controller:

```python
$ sudo cp tray.py /usr/local/bin/ite_tray.py
```

- Open `Startup Applications Preferences` and add the application
  - Name: `ite_tray`
  - Command: `/usr/bin/python3 /usr/local/bin/ite_tray.py`

- Reboot



# Extra: Lightbar for Stellaris 15

- Make sure `tuxedo_keyboard` is installed.

```
sudo crontab -e
```

- Add this line then save

```
@reboot echo 1 > /sys/devices/platform/tuxedo_keyboard/leds/lightbar_animation::status/brightness
```

- Reboot

