import bluetooth
ble = bluetooth.BLE()
ble.active(True)
#BT MAC Address
addr_type, addr = ble.config('mac')
mac = ':'.join('{:02X}'.format(b) for b in addr)
print("BLE MAC Address:", mac)
#BT Advertising Checker
ble.gap_advertise(100, b'\x02\x01\x06\x03\x03\xAA\xFE')
print("Advertising")