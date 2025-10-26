#!/usr/bin/python

from smbus2 import SMBus
import time

DEVICE_ADDRESS = 0x20      #7 bit address (will be left shifted to add the read write bit)
DEVICE_REG_MODE1 = 0x00

status = 1

# --- Hauptprogramm ---
try:
    while True:
        if status:
            SMBus(1).write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0x00)
            print("Relais aus")
        else:
            SMBus(1).write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0x255)
            print("Relais ein")
                
        status ^= 1   
        time.sleep(2)

except KeyboardInterrupt:
    print("\nBeendet vom Benutzer.")
    # --- Aufräumen ---
    SMBus(1).write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0x00)
    print("GPIO freigegeben, Script beendet.")
