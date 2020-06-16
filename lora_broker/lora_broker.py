
#  this script listens for LoRa messages received by a Lopy connected via USB
#  and forwards those messages to a remote PostgreSQL DB

import serial
import sys
import psycopg2

# open a serial connection
ser = serial.Serial('/dev/ttyACM0',baudrate=115200,bytesize=8,parity='N',stopbits=1,timeout=1)

# print actual serial connection
print("Listening to serial connection on: ",ser.name)


# read received Lopy messages via serial connection
def lopy_usb():
	''' This fuction reads LoRa messages received by a LoPy via USB '''
	
	while True:
		msg_raw = ser.read(100)
		if msg_raw != b'':
			msg = msg_raw.decode()
			msg = msg.strip("'b")
			msg = msg.replace("'", "")
			yield(msg)
	return


# send msg to postgreSQL DB
for lopy_data in lopy_usb():
	try:
		con = psycopg2.connect(user = "username",
					password = "password",
					host = "127.0.0.1",
					port = "5432",
					database = "sensors")
		cur = con.cursor()
		SQL = "INSERT INTO lora_feed (data) VALUES (%s);"
		new_data = (lopy_data, )
		cur.execute(SQL, new_data)
		con.commit()
		cur.close()
		con.close()
		print("DB insert successful: %s" % (lopy_data))
	# add some error handling
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
		print("DB insert unsuccessful: %s" % (lopy_data))


