#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
raspi_wechselrichter_i2c_csv.py
Ansteuerung der IO-Ports des Kostal Wechselrichters für externe Batteriesteuerung
Strompreis (hoch/niedrig) wird ueber eine csv Datei eingelesen
IO-Ports werden ueber Relaiskarte mit I2C und XL9535 bedient
"""

#!/usr/bin/env python3
import csv
import os
import time
import signal     # fuer Abfrage strg+c
import sys
#import RPi.GPIO as GPIO   # fuer Nutzung RPi GPIO Pin
from smbus2 import SMBus   # fuer Nutzung RPi I2C Bus
from datetime import datetime, timedelta

# --- Einstellungen ---
CSV_FILE = "strompreise.csv"   # Tabelle mit Zeitblöcken
GPIO_PIN = 17                  # GPIO-Pin (BCM-Nummerierung)
CHECK_INTERVAL = 60            # Sekündlich prüfen ob Änderung in CSV
STOP_FILE = "stop.txt"         # Wenn Datei existiert → Programm beendet sich

"""
Abschnitt fuer GPIO Nutzung
# Variante 1: PIN=high -> Relais ein (über BC547 Transistor verbunden)
#REL_ON = GPIO.HIGH
#REL_OFF = GPIO.LOW
# Variante 2: PIN=low -> Relais ein (direkt verbunden)
#REL_ON = GPIO.LOW
#REL_OFF = GPIO.HIGH
# --- GPIO Setup ---
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(GPIO_PIN, GPIO.OUT)
#GPIO.output(GPIO_PIN, REL_OFF)    # Relaisansteuerung - aus
"""

"""
Abschnitt fuer I2C Bus Nutzung
"""
DEVICE_ADDRESS   = 0x20    # Adresse - sudo i2cdetect -y 1
DEVICE_REG_MODE1 = 0x06    # Registeradresse Konfigurationsregister
DEVICE_REG_OUT1  = 0x02    # Registeradresse Ausgaberegister
DEVICE_MODE_OUT  = 0x00    # Modus Konfgurationsregister -> Ausgabe
KOSTAL_INTERN    = 0x00    # KOSTAL interne Batteriesteuerung
KOSTAL_LOCKED    = 0x01    # KOSTAL Batterienutzung gesperrt
KOSTAL_DISC_100  = 0x02    # KOSTAL Entladen 100% Batterieleistung -> 5,5kw?
KOSTAL_CHG_100   = 0x03    # KOSTAL Laden 100% Batterieleistung -> 5,5kw?
KOSTAL_DISC_25   = 0x04    # KOSTAL Entladen 25% Batterieleistung -> 1,375kw?
KOSTAL_CHG_25    = 0x05    # KOSTAL Laden 25% Batterieleistung -> 1,375kw?
KOSTAL_DISC_50   = 0x06    # KOSTAL Entladen 50% Batterieleistung -> 2,75kw?
KOSTAL_CHG_50    = 0x07    # KOSTAL Laden 50% Batterieleistung -> 2,75kw?
KOSTAL_DISC_75   = 0x08    # KOSTAL Entladen 75% Batterieleistung -> 4,125kw?
KOSTAL_CHG_75    = 0x09    # KOSTAL Laden 750% Batterieleistung -> 4,125kw?


# --- Globale Variablen ---
stromtabelle = {}
last_mtime = None
running = True

# --- Signal Handler (CTRL+C) ---
def signal_handler(sig, frame):
    global running
    running = False
    print("\nBeende Script...")
signal.signal(signal.SIGINT, signal_handler)

# --- Hilfsfunktion: CSV mit allen 96 Slots erzeugen ---
def create_default_table():
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        t = datetime.strptime("00:00", "%H:%M")
        for _ in range(96):  # 96 Viertelstunden
            writer.writerow([t.strftime("%H:%M"), "teuer"])
            t += timedelta(minutes=15)
    print(f"Neue CSV-Datei '{CSV_FILE}' mit Standardwerten erstellt.")

# --- Tabelle laden ---
def load_table():
    global stromtabelle, last_mtime
    try:
        mtime = os.path.getmtime(CSV_FILE)
        if last_mtime is None or mtime != last_mtime:
            with open(CSV_FILE, newline="", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=";")
                new_table = {}
                for row in reader:
                    if len(row) < 2:
                        continue
                    zeit, status = row[0].strip(), row[1].strip().lower()
                    new_table[zeit] = status in ("1", "true", "ja", "günstig")
                stromtabelle = new_table
                last_mtime = mtime
                print(f"Tabelle neu geladen: {len(stromtabelle)} Einträge")
    except FileNotFoundError:
        create_default_table()
        load_table()
    except Exception as e:
        print(f"Fehler beim Laden der Tabelle: {e}")

# --- Funktion: aktuellen 15min Slot bestimmen ---
def current_slot():
    now = datetime.now()
    # Stunde:Minute, gerundet auf 15 Minuten
    minute = (now.minute // 15) * 15
    slot = f"{now.hour:02d}:{minute:02d}"
    return slot

# --- Hauptschleife ---
print("Starte Strompreis-Kontrolle...")
load_table()

# --- I2C Bus intialisieren ---
bus = SMBus(1)  # erstelle Instanz
bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, DEVICE_MODE_OUT)


while running:
    # Tabelle ggf. neu laden
    load_table()

    slot = current_slot()
    status = stromtabelle.get(slot, False)

    if status:
#        GPIO.output(GPIO_PIN, REL_ON)
#        print(f"{slot} → Strompreis günstig → GPIO {GPIO_PIN} = {REL_ON} → Relais ein")
         bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_OUT1, KOSTAL_CHG_50)
         print("Laden aktv")
    else:
#        GPIO.output(GPIO_PIN, REL_OFF)
#        print(f"{slot} → Strompreis teuer   → GPIO {GPIO_PIN} = {REL_OFF} → Relais aus")
         bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_OUT1, KOSTAL_INTERN)
         print("Laden inaktiv")
    time.sleep(CHECK_INTERVAL)

# --- Aufräumen ---
#GPIO.output(GPIO_PIN, REL_OFF)    # Relais aus
#GPIO.cleanup()
#print("GPIO freigegeben, Script beendet.")
# --- Aufräumen ---
print("\nBeendet vom Benutzer.")
bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_OUT1, KOSTAL_INTERN)
bus.close()
print("bus freigegeben, Script beendet.")
