import asyncio
from bleak import BleakClient, BleakScanner

# Nordic UART Service UUIDs
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # ESP32 → Laptop (Notify)
UART_RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Laptop → ESP32 (Write)

async def main():
    print("Scanning for Spider-Hex...")
    devices = await BleakScanner.discover()

    esp = None
    for d in devices:
        if d.name == "Spider-Hex":
            esp = d
            break

    if esp is None:
        print("ESP32-BLE not found")
        return

    print("Found:", esp.address)

    async with BleakClient(esp.address) as client:
        print("Connected to ESP32")

        def notification_handler(_, data):
            print("ESP32:", data.decode().strip())

        # Enable notifications
        await client.start_notify(UART_TX_UUID, notification_handler)

        print("Type messages. Ctrl+C to exit.")

        while True:
            msg = input("> ")
            await client.write_gatt_char(UART_RX_UUID, msg.encode())

asyncio.run(main())
