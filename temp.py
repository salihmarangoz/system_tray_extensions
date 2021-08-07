
# pip install nvitop pyspectator psutil ite8291r3-ctl

from pyspectator.processor import Cpu
from nvitop.core import Device
from time import sleep
import psutil
from ite8291r3_ctl import ite8291r3

gpu = Device(0)
ite = ite8291r3.get()


def get_gpu_temp():
    return gpu.temperature()

def get_cpu_temp():
    return Cpu(monitoring_latency=1).temperature

def get_bat_percentage():
    return psutil.sensors_battery().percent

ite.set_effect(ite8291r3.effects["breathing"]())

while True:
    print("gpu:", get_gpu_temp())
    print("cpu:", get_cpu_temp())
    print("bat:", get_bat_percentage())
    sleep(1)
