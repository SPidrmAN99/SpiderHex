import time
import bluetooth
from Advertise_Pair_V4 import BLEUART
import Menu_V4

print("Booting Spider-Hex...")

ble = bluetooth.BLE()
uart = BLEUART(ble)

while not uart.is_connected():
    time.sleep(0.2)

handshake_done = False

while True:
    cmd = uart.read()
    if not cmd:
        time.sleep(0.05)
        continue

    if cmd == "CLIENT_READY" and not handshake_done:
        uart.send("SERVER_READY")
        Menu_V4.show_menu(uart.send)
        uart.send("SERVER_IDLE")
        handshake_done = True
        continue

    if not handshake_done:
        continue

    Menu_V4.handle_choice(cmd, uart.send)

