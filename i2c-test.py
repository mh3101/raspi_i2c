# Bibliotheken laden
from machine import Pin, I2C

# Initialisierung I2C-Pins
i2c_sda = Pin(20)
i2c_scl = Pin(21)

# Initialisierung I2C
i2c = I2C(0,sda=i2c_sda,scl=i2c_scl,freq=100000)

# I2C-Bus-Scan
print('Scan I2C Bus...')
devices = i2c.scan()

# Scanergebnis ausgeben
if len(devices) == 0:
    print('Kein I2C-Gerät gefunden!')
else:
    print('I2C-Geräte gefunden:', len(devices))
    for device in devices:
        print('Dezimale Adresse:', device, '| Hexadezimale Adresse:', hex(device))
