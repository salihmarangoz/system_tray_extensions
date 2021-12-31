import gi #check_import
gi.require_version('Gtk', '3.0') #check_import
gi.require_version('AppIndicator3', '0.1') #check_import
from gi.repository import Gtk, AppIndicator3, GLib #check_import
import signal #check_import
import time #check_import
import threading #check_import
import os #check_import

class Indicator():
    def __init__(self):
        self.app = 'battery_power_use'
        iconpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'flashlight.png')
        self.indicator = AppIndicator3.Indicator.new(self.app, iconpath, AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_menu(self.create_menu())
        self.update = threading.Thread(target=self.show_indicator)
        self.update.setDaemon(True)
        self.update.start()

    def create_menu(self):
        menu = Gtk.Menu()
        item_quit = Gtk.MenuItem(label='Dismiss')
        item_quit.connect('activate', self.stop)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def show_indicator(self):
        while True:
            with open('/sys/class/power_supply/BAT0/current_now', 'r', encoding='utf-8') as f:
                out = f.readlines()
                current_now = out[0].lower().strip()
            with open('/sys/class/power_supply/BAT0/voltage_now', 'r', encoding='utf-8') as f:
                out = f.readlines()
                voltage_now = out[0].lower().strip()
            with open('/sys/class/power_supply/BAT0/status', 'r', encoding='utf-8') as f:
                out = f.readlines()
                status = out[0].lower().strip()

            if status != "discharging":
                self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
                time.sleep(1)
                continue

            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            power_now = (float(current_now)/10**6) * (float(voltage_now)/10**6)
            mention = str(round(power_now, 2)) + "W"
            GLib.idle_add(self.indicator.set_label, mention, self.app, priority=GLib.PRIORITY_LOW)
            time.sleep(1)

    def stop(self, source):
        Gtk.main_quit()

Indicator()
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()