#!/usr/bin/python

from smbus2 import SMBus
import time

DEVICE_ADDRESS = 0x20      # 7 bit address (will be left shifted to add the read write bit)
DEVICE_REG_MODE1 = 0x06    # Konfigurationsregister
DEVICE_MODE_OUT = 0x00     # Konfgurationsregister -> Ausgabe
DEVICE_REG_OUT1 = 0x02     # Ausgaberegister

status = 1

bus = SMBus(1)

bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, DEVICE_MODE_OUT)

# --- Hauptprogramm ---
try:
    while True:
        if status:
            bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_OUT1, 0x00)
            print("Relais aus")
        else:
            bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_OUT1, 0x255)
            print("Relais ein")
                
        status ^= 1   
        time.sleep(2)

except KeyboardInterrupt:
    print("\nBeendet vom Benutzer.")
    # --- Aufräumen ---
    bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_OUT1, 0x00)
    bus.close()
    print("bus freigegeben, Script beendet.")
