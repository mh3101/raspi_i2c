#!/usr/bin/python

import smbus
import time

bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

DEVICE_ADDRESS = 0x20      #7 bit address (will be left shifted to add the read write bit)
DEVICE_REG_MODE1 = 0x00

status = 1

#Write a single register
bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0x00)

# --- Hauptprogramm ---
try:
    while True:
        if status:
            bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0x00)
            print("Relais aus")
        else:
            bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0x255)
            print("Relais ein")
                
        status ^= 1   
        time.sleep(1)

except KeyboardInterrupt:
    print("\nBeendet vom Benutzer.")
    # --- Aufräumen ---
    bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0x00)
    print("GPIO freigegeben, Script beendet.")
