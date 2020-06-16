#!/usr/bin/env python
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

from pytrack import Pytrack
from LIS2HH12 import LIS2HH12
from network import LoRa
import machine
import pycom
import socket
import time
import ubinascii

py = Pytrack()
acc = LIS2HH12()

# unique id (last 4 of mac) for message
id = ubinascii.hexlify(machine.unique_id()).decode()[8:12]

# type of sensor
type = "accel"

# creat lora socket
lora = LoRa(mode=LoRa.LORA, region=LoRa.US915,
            frequency=902000000,
            tx_power=20,
            sf=12,
            power_mode=LoRa.TX_ONLY)

sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
sock.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)

# enable the activity/inactivity interrupts
# set the accelereation threshold to 1500mG (1.5G) and the min duration to 200ms
acc.enable_activity_interrupt(1500, 200)

# check for activity
def activity_detection():
    '''This function will alert when sensor acceleration exceeds 1.5G'''
    while True:
        if acc.activity() == "Activity interrupt" :
            msg = '{ "id":"%s", "type":"%s", "activity":"device moved" }' % (id, type)
            print(msg)
            time.sleep_ms(500)
            sock.send(msg)
