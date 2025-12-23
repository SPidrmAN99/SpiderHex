import asyncio
from bleak import BleakClient, BleakScanner

UART_TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"


async def main():
    print("Scanning for Spider-Hex...")
    devices = await BleakScanner.discover()

    esp = next((d for d in devices if d.name == "Spider-Hex"), None)
    if not esp:
        print("ESP32 not found")
        return

    print("Found:", esp.address)

    async with BleakClient(esp.address) as client:
        print("Connected")

        def notify(_, data):
            print(data.decode().rstrip())

        await client.start_notify(UART_TX_UUID, notify)

        while True:
            cmd = input("> ")
            await client.write_gatt_char(
                UART_RX_UUID,
                (cmd + "\n").encode()
            )


asyncio.run(main())
