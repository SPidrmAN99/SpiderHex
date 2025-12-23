import time
import bluetooth
from Advertise_Pair_V2 import BLEUART
import Menu_V2

timeout = 60  # seconds

print("Booting Spider-Hex...")
print("Please connect before Time out: ", timeout, "seconds")

# Wait for BLE connection with timeout

ble = bluetooth.BLE()
uart = BLEUART(ble)

start = time.ticks_ms()
while not uart.is_connected():
    if time.ticks_diff(time.ticks_ms(), start) > timeout * 1000:
        print("No BLE connection detected.", timeout, "seconds Timed out.")
        break
    time.sleep(0.2)

if uart.is_connected():
    #print("Device connected!")
    # Run motion control menu safely
    Menu_V2.menu()
    print("Main script completed. System idle.")