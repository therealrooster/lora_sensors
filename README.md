# lora_sensor summary
This repo includes code for (4) different types of LoPy (with Pytrack) sensors: PIR, Ultrasonic, Reed Switch, and Accelerometer.  It also includes a python script which has a raspberry Pi 3B+ acting as a LoRa forwarder to a remote PostgreSQL server.

# PIR sensor
Utilized a SparkFun OpenPIR (SEN-13968). Outputs sensor alert via LoRa in json format.

# Ultrasonic sensor
Utilized LV-MaxSonarEZ.  This requires a MAX3232 transceiver breakout to convert the RS3232 (ultrasonic output) to TTL. Outputs sensor alert via LoRa in json format.

# Reed Switch
Utilized a magnetic door switch from SparkFun (COM-13247).  Required a 4k7 resistor on the positive side of the switch. Outputs sensor alert via LoRa in json format.

# Accelerometer
Utilized the built in accelerometer of the Pytrack.  Outputs sensor alert via LoRa in json format.

# LoPy gateway
Receives output messages of the LoPy sensors via LoRa.

# lora broker (raspi)
LoPy gateway is plugged directly into the raspi via USB.  Forwards received LoPy messages to a remote PostgreSQL DB.  Requires: python3, postgresql, psycopg2, and libpq-dev.
