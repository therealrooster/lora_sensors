#!/usr/bin/env python
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

import time
import pycom
import machine
import socket
import ubinascii
from machine import UART
from network import LoRa

# create uart channel
uart = UART(1, 9600)
uart.init(9600, bits=8, parity=None, stop=1)

# unique id (last 4 of mac) for message
id = ubinascii.hexlify(machine.unique_id()).decode()[8:12]

# type of sensor
type = "ultra"

# creat lora socket
lora = LoRa(mode=LoRa.LORA, region=LoRa.US915,
            frequency=902000000,
            tx_power=20,
            sf=12,
            power_mode=LoRa.TX_ONLY)

sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
sock.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)

# provide distance when readings vary > 6 inches
def distance_generator():
    '''This function will provide a distance when it varies'''
    last_dist = 0
    while True:
        time.sleep_ms(500)
        new_dist_raw = uart.read()
        new_dist = int(str(new_dist_raw).split('\\rR')[-2])
        if abs(last_dist - new_dist) > 6:
            last_dist = new_dist
            yield(last_dist)

    return

# create and send lora packet
for distance in distance_generator():
    msg = '{ "id":"%s", "type":"%s", "activity":"new distance: %din" }' % (id, type, distance)
    print(msg)
    time.sleep_ms(300)
    sock.send(msg)
