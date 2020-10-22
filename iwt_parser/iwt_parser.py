# This script connects to a remote IWT Coyote Server and
# subscribes to sensor_activity_alarm.  Desired fields
# within the received XML is then stripped into a JSON string.
# The JSON string is then inserted into a remote PG DB.

import psycopg2
import os
import socket
import time
import sys
from bs4 import BeautifulSoup
import pandas as pd
from signal import signal, SIGINT
from sys import exit
import re
from termcolor import colored, cprint

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# mProv server:
ip = "10.100.2.52"
port = 2502
usr = "username"
pwd = "password"

# def graceful close handler
def handler(signal_received, frame):
	print("\n\nCTRL-C Deteced.  Closing socket with IWT server")
	s.close()
	exit(0)

# tell python to run the handler() when CTRL-C is received
signal(SIGINT, handler)

# clear bash screen
os.system('clear')

# login and subscribe to alarms
cprint("Attempting connection with IWT server: %s:%s" % (ip, port), 'blue', attrs=['bold'])
time.sleep(2)

s.connect((ip,port))
sub = '<?xml version="1.0" encoding="UTF-8"?><mprovclient user="%s" password="%s"><call name="subscribe"><params><array><value type="string">sensor_activity_alarm</value></array></params></call>' % (usr, pwd)
s.sendall(sub.encode())

# verify session was created
while True:
	msg = s.recv(524288).decode()
	if msg.startswith("<?xml"):
		msg = ""
		pass
	elif msg.startswith("<mprovserver"):
		msg = msg.strip('mprovserver session_id="')
		msg = re.sub('[^0-9]','', msg)
		if int(msg) > 0:
			cprint("\n\nConnection success!\nSession ID: %s" % (msg), 'green', attrs=['bold'])
			print("\n\nStanding by for alarm messages...")
			break
	else:
		msg = ""
		pass

# receive data
def iwt_data():
	cnt = 1
	msgstr = ""
	while True:
		msg = s.recv(1048576).decode()
		if cnt > 2:
			msgstr += msg
			if msg.endswith("</message>"):
				if msgstr.startswith("<message"):
					### MESSAGE HEADER
					bs = BeautifulSoup(msgstr, 'xml')
					message = bs.find('message')
					params = message.find('params')
					alarm_status = params.find('value', {'hint': 'alarm_status'}).text
					if alarm_status.endswith("(Alarm Complete)"):
						#timestamp = params.find('value', {'hint': 'timestamp'}).text
						pan_id = params.find('value', {'hint': 'pan_id'}).text
						node_id = params.find('value', {'hint': 'node_id'}).text
						id = pan_id + "-" + node_id
						duration = params.find('value', {'hint': 'duration'}).text
						lat = params.find('value', {'hint': 'latitude'}).text
						lon = params.find('value', {'hint': 'longitude'}).text
						elev = 0
						pgmsg = [id, alarm_status, duration, lat, lon, elev]
						yield(pgmsg)
					else:
						pass
				else:
					pass
				msgstr = ""
		cnt += 1
	return

print(f"MESSAGE_STATUS\tID\t  SENSOR_ACTIVITY\t\t\t\t\t\t\t\tDUR\tLATITUDE\tLONGITUDE\tELEVATION")
status_s = "Successful"
status_u = "Unsuccessful"

# get the messages
for data in iwt_data():
	act = "{0:70}".format(data[1])
	rows = []

	# attempt PG connection
	try:
		con = psycopg2.connect(user = "username",
					password = "password",
					host = "10.100.2.51",
					port = "5432",
					database = "sensors")

	# if error detected, save messages data to csv, and print unsuccessful
	except (Exception, psycopg2.OperationalError) or (Exception, psycopg2.DatabaseError) as error:
		tdate = time.strftime("%Y%m%d")
		timestr = time.strftime("%Y%m%d-%H%M%S")
		cols = ["TIMESTAMP", "ID", "ACTIVITY", "DURATION", "LATITUDE", "LONGITUDE", "ELEVATION", "ERROR"]
		rows.append({"TIMESTAMP": timestr, "ID": data[0], "ACTIVITY": data[1], "DURATION": data[2], "LATITUDE": data[3], "LONGITUDE": data[4], "ELEVATION": data[5], "ERROR": error})
		outname = f'{tdate}.csv'
		outdir = './errors'
		fname = os.path.join(outdir, outname)
		df = pd.DataFrame(rows, columns=cols)

		if not os.path.exists(outdir):
			os.mkdir(outdir)

		df.to_csv(fname, mode='a', header=False, index=False)
		print(f"{status_u}\t{data[0]}\t  {act}\t{data[2]}\t{data[3]}\t{data[4]}\t{data[5]}")

	# try DB insert
	else:
		# uncomment below to force a lat, long, elev for a specific sensor:
		#if data[0] == "65535-2":
			#cur = con.cursor()
			#data[3] = 35.4892641
			#data[4] = -116.4635333
			#data[5] = 1068.175858
			#cur.execute("INSERT INTO iwt_feed (sensor_id,sensor_activity,sensor_duration,latitude,longitude,elevation) VALUES (%s,%s,%s,%s,%s,%s)", (data[0],data[1],data[2],data[3],data[4],data[5]))
			#con.commit()
			#cur.close()
			#con.close()
			#print(f"{status_s}\t{data[0]}\t  {act}\t{data[2]}\t{lat}\t{long}\t{elev}")

		cur = con.cursor()
		cur.execute("INSERT INTO iwt_feed (sensor_id,sensor_activity,sensor_duration,latitude,longitude,elevation) VALUES (%s,%s,%s,%s,%s,%s)", (data[0],data[1],data[2],data[3],data[4],data[5]))
		con.commit()
		cur.close()
		con.close()
		print(f"{status_s}\t{data[0]}\t  {act}\t{data[2]}\t{data[3]}\t{data[4]}\t{data[5]}")
