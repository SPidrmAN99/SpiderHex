import asyncio
from bleak import BleakClient, BleakScanner

UART_TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

server_idle = asyncio.Event()
server_idle.clear()


async def main():
    print("Scanning for Spider-Hex...")
    devices = await BleakScanner.discover()

    esp = next((d for d in devices if d.name == "Spider-Hex"), None)
    if not esp:
        print("ESP32 not found")
        return

    async with BleakClient(esp.address) as client:
        print("Connected, subscribing...")

        def notify(_, data):
            msg = data.decode().rstrip()
            print(msg)

            if msg == "SERVER_IDLE":
                server_idle.set()
            elif msg == "SERVER_BUSY":
                server_idle.clear()

        await client.start_notify(UART_TX_UUID, notify)

        await asyncio.sleep(0.2)
        await client.write_gatt_char(UART_RX_UUID, b"CLIENT_READY\n")

        await server_idle.wait()
        print("Ready for commands.")

        while True:
            await server_idle.wait()
            cmd = input("> ").strip()
            if not cmd:
                continue

            server_idle.clear()
            await client.write_gatt_char(
                UART_RX_UUID, (cmd + "\n").encode()
            )


asyncio.run(main())
