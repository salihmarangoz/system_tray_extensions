
# pip install nvitop pyspectator psutil ite8291r3-ctl

from pyspectator.processor import Cpu
from nvitop.core import Device
from time import sleep
import psutil
from ite8291r3_ctl import ite8291r3

import math

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

gpu = Device(0)
ite = ite8291r3.get()


def get_gpu_temp():
    return gpu.temperature()

def get_cpu_temp():
    return Cpu(monitoring_latency=1).temperature

def get_bat_percentage():
    return psutil.sensors_battery().percent

ite.set_effect(ite8291r3.effects["breathing"]())


f_keys = [(5,1),(5,2),(5,3),(5,4),(5,5),(5,6),(5,7),(5,8),(5,9),(5,10)]
number_keys = [(4,1),(4,2),(4,3),(4,4),(4,5),(4,6),(4,7),(4,8),(4,9),(4,10)]
numlock_keys = [(1,15), (1,16), (1,17), (2,15), (2,16), (2,17), (3,15), (3,16), (3,17)]


def map_value_to_keys(value, min_value, max_value, keys, color_map):
    value_int = value // 10
    for i in range(min(9,value_int)):
        if i==value_int-1:
            last_color = int(255-((i+2)*10-value)*255/10)
            color_map[keys[i]] = (last_color, 0, 0)
        else:
            color_map[keys[i]] = (255, 0, 0)

def map_value_to_keys2(value, min_value, max_value, keys, color_map):
    value_int = value // 10
    last_color = 1-(value % 10)/10
    print(last_color)
    last_color = int(sigmoid(last_color/(1-last_color))*255)
    color_map[keys[value_int]] = (255-last_color, 255-last_color, 255-last_color)
    color_map[keys[value_int-1]] = (last_color, last_color, last_color)


while True:
    gpu_temp = get_gpu_temp()
    cpu_temp = get_cpu_temp()
    bat_perc = get_bat_percentage()

    color_map = {}

    map_value_to_keys2(cpu_temp, 1, 1, f_keys, color_map)
    map_value_to_keys2(gpu_temp, 1, 1, number_keys, color_map)
    map_value_to_keys(bat_perc, 1, 1, numlock_keys, color_map)


    ite.set_key_colors(color_map)
    ite.set_brightness(50)
    sleep(0.5)

