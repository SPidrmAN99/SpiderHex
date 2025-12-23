import time
import bluetooth
from Advertise_Pair_V4 import BLEUART
import Menu_V4

print("Booting Spider-Hex...")

ble = bluetooth.BLE()
uart = BLEUART(ble)

timeout = 60
start = time.ticks_ms()

while not uart.is_connected():
    if time.ticks_diff(time.ticks_ms(), start) > timeout * 1000:
        print("BLE timeout. System idle.")
        break
    time.sleep(0.2)

if uart.is_connected():
    uart.send("Connected to Spider-Hex")
    time.sleep(0.5)  # allow notify subscription
    Menu_V4.show_menu(uart.send)

    while True:
        cmd = uart.read()
        if cmd:
            Menu_V4.handle_choice(cmd, uart.send)
