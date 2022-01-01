#!/usr/bin/env python

import dbus #check_import
from gi.repository import GLib #check_import
from dbus.mainloop.glib import DBusGMainLoop #check_import
import signal #check_import
import sys #check_import
#import logging # DONT USE LOGGING HERE

def handle_suspend_callback(mode):
    if mode == 0:
        print("resume", flush=True)
    elif mode == 1:
        print("suspend", flush=True)

def handle_upower_callback(*args):
    if 'LidIsClosed' in args[1]:
        if args[1]['LidIsClosed'] == 0:
            print("lid_opened", flush=True)
        elif args[1]['LidIsClosed'] == 1:
            print("lid_closed", flush=True)

    if 'OnBattery' in args[1]:
        if args[1]['OnBattery'] == 0:
            print("on_ac", flush=True)
        elif args[1]['OnBattery'] == 1:
            print("on_battery", flush=True)

DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

bus.add_signal_receiver(
    handle_suspend_callback,
    'PrepareForSleep',
    'org.freedesktop.login1.Manager',
    'org.freedesktop.login1'
)

bus.add_signal_receiver(
    handle_upower_callback,
    'PropertiesChanged',
    'org.freedesktop.DBus.Properties',
    path='/org/freedesktop/UPower',
)

def signal_handler(*args):
    print("exit")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
loop = GLib.MainLoop()
loop.run()