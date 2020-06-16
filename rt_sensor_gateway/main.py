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
from machine import UART
from network import LoRa
import socket

uart = UART(1, 9600)
uart.init(9600, bits=8, parity=None, stop=1)

lora = LoRa(mode=LoRa.LORA, region=LoRa.US915,
            frequency=902000000,
            tx_power=20,
            sf=12,
            power_mode=LoRa.ALWAYS_ON)

sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
sock.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)

while True:
   msg = sock.recv(128)
   print(msg)
