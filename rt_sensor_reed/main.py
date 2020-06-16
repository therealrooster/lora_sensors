#!/usr/bin/env python
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

from machine import Pin
from network import LoRa
from network import WLAN
import pycom
import time
import machine
import socket
import ubinascii

# disable wifi
wlan = WLAN()
wlan.deinit()

# create sensor pin
reed = Pin('P10',mode=Pin.IN, pull=None)

# unique id (last 4 of mac) for message
id = ubinascii.hexlify(machine.unique_id()).decode()[8:12]

# type of sensor
type = "reed"

# creat lora socket
lora = LoRa(mode=LoRa.LORA, region=LoRa.US915,
            frequency=902000000,
            tx_power=20,
            sf=12,
            power_mode=LoRa.TX_ONLY)

sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
sock.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)

# check for activity
def activity_generator():
    '''This function will check reed state'''
    reed_state = reed()

    while True:
        if reed() != reed_state:
            if reed_state == 0:
                reed_state = 1
                yield("open")
            else:
                reed_state = 0
                yield("closed")

        time.sleep_ms(500)

# create and send lora packet
for activity in activity_generator():
    msg = '{ "id":"%s", "type":"%s", "activity":"%s" }' % (id, type, activity)
    print(msg)
    sock.send(msg)
