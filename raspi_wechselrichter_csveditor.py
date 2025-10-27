# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
raspi_wechselrichter_csveditor.py
Bearbeiten einer csv-Datei mit Auswahl der Uhrzeit in 15min-Schritten zum Eintragen von Status teuer oder günstig
"""
import csv
import os
from datetime import datetime, timedelta

CSV_FILE = "strompreise.csv"

def ensure_table():
    """Erzeugt die Tabelle falls sie noch nicht existiert."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            t = datetime.strptime("00:00", "%H:%M")
            for _ in range(96):  # 96 Viertelstunden
                writer.writerow([t.strftime("%H:%M"), "teuer"])
                t += timedelta(minutes=15)

def load_table():
    table = {}
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if len(row) < 2:
                continue
            zeit, status = row[0].strip(), row[1].strip().lower()
            table[zeit] = status
    return table

def save_table(table):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        for zeit in sorted(table.keys()):
            writer.writerow([zeit, table[zeit]])

def show_table(table):
    print("\nAktuelle Strompreis-Tabelle (günstig/teuer):")
    zeiten = sorted(table.keys())
    for i, zeit in enumerate(zeiten, 1):
        print(f"{zeit:>5}  →  {table[zeit]}")
        if i % 12 == 0:  # Nach 3 Stunden Pause für Übersicht
            print()
    print()

def edit_slot(table):
    zeit = input("Zeit im Format HH:MM (z.B. 14:30): ").strip()
    if zeit not in table:
        print("Ungültige Zeit. Bitte im 15-Minuten-Raster bleiben!")
        return
    neuer_status = input("Neuer Status (günstig/teuer): ").strip().lower()
    if neuer_status not in ("günstig", "teuer"):
        print("Ungültiger Status! Nur 'günstig' oder 'teuer'.")
        return
    table[zeit] = neuer_status
    print(f"Slot {zeit} geändert zu '{neuer_status}'.")

def main():
    ensure_table()
    table = load_table()

    while True:
        print("\n--- Strompreis-Editor ---")
        print("1) Tabelle anzeigen")
        print("2) Slot bearbeiten")
        print("3) Speichern")
        print("4) Beenden")
        choice = input("Auswahl: ").strip()

        if choice == "1":
            show_table(table)
        elif choice == "2":
            edit_slot(table)
        elif choice == "3":
            save_table(table)
            print("Änderungen gespeichert.")
        elif choice == "4":
            print("Beende Editor...")
            break
        else:
            print("Ungültige Eingabe!")

if __name__ == "__main__":
    main()

