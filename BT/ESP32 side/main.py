import time
import bluetooth
from Advertise-Pair import BLEUART
import Menu

print("Booting Spider-Hex...")

ble = bluetooth.BLE()
uart = BLEUART(ble)

# Wait for BLE connection
print("Waiting for BLE connection...")
while not uart.is_connected():
    time.sleep(0.2)

print("Device connected!")
Menu.start()
