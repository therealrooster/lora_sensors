
#  this script listens for LoRa messages received by a Lopy connected via USB
#  and forwards those messages to a remote PostgreSQL DB

import serial
import sys
import psycopg2
import os
import json

# clear terminal
os.system('clear')

# open a serial connection
ser = serial.Serial('/dev/ttyACM0',baudrate=115200,bytesize=8,parity='N',stopbits=1,timeout=1)

# print actual serial connection
print("Listening to serial connection on: ",ser.name)


# read received Lopy messages via serial connection
def lopy_usb():
	''' This fuction reads LoRa messages received by a LoPy via USB '''

	while True:
		msg_raw = ser.read(75)
		if msg_raw != b'':
			msg = msg_raw.decode()
			msg = msg.strip("'b")
			msg = msg.replace("'", "")
			msg = json.loads(msg)
			yield(msg)
		else:
			pass
	return

# send msg to postgreSQL DB
for lopy_data in lopy_usb():
	con = psycopg2.connect(user = "username",
			password = "password",
			host = "10.100.2.51",
			port = "5432",
			database = "sensors")
	nd = lopy_data
	try:
		if nd["id"] == "6cb4":
			lat = 35.4894254
			long = -116.4656758
			elev = 1062.193761
			cur = con.cursor()
			cur.execute("INSERT INTO lora_feed (sensor_id,sensor_type,sensor_activity,latitude,longitude,elevation) VALUES (%s,%s,%s,%s,%s,%s)", (nd["id"],nd["type"],nd["activity"],lat,long,elev))
			con.commit()
			cur.close()
			con.close()
			print("Successful: %s %s %s %s %s %s" % (nd["id"],nd["type"],nd["activity"],lat,long,elev))
		elif nd["id"] == "6784":
			lat = 35.4894754
			long = -116.4664556
			elev = 1060.885953
			cur = con.cursor()
			cur.execute("INSERT INTO lora_feed (sensor_id,sensor_type,sensor_activity,latitude,longitude,elevation) VALUES (%s,%s,%s,%s,%s,%s)", (nd["id"],nd["type"],nd["activity"],lat,long,elev))
			con.commit()
			cur.close()
			con.close()
			print("Successful: %s %s %s %s %s %s" % (nd["id"],nd["type"],nd["activity"],lat,long,elev))
		else:
			lat = 0
			long = 0
			elev = 0
			cur = con.cursor()
			cur.execute("INSERT INTO lora_feed (sensor_id,sensor_type,sensor_activity,latitude,longitude,elevation) VALUES (%s,%s,%s,%s,%s,%s)", (nd["id"],nd["type"],nd["activity"],lat,long,elev))
			con.commit()
			cur.close()
			con.close()
			print("Successful: %s %s %s %s %s %s" % (nd["id"],nd["type"],nd["activity"],lat,long,elev))

	# add some error handling for db insert
	except (Exception, psycopg2.DatabaseError) as error:
		print("Unsuccessful: %s\n%s" % (lopy_data, error))
