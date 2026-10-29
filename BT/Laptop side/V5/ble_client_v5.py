import asyncio
from bleak import BleakScanner, BleakClient

# ===============================
# CONFIG
# ===============================

DEVICE_NAME = "Spider-Hex"

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_UUID      = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # write
UART_TX_UUID      = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # notify


# ===============================
# BLE CLIENT
# ===============================

async def main():
    print("Scanning for Spider-Hex...")

    device = None
    devices = await BleakScanner.discover(timeout=5.0)

    for d in devices:
        if d.name == DEVICE_NAME:
            device = d
            break

    if not device:
        print("ERROR: Spider-Hex not found")
        return

    async with BleakClient(device) as client:
        print("Connected, subscribing...")

        # -------------------------------
        # Notification handler
        # -------------------------------
        def on_notify(_, data: bytearray):
            try:
                msg = data.decode(errors="ignore").strip()
                if msg:
                    print(msg)
            except Exception:
                pass

        await client.start_notify(UART_TX_UUID, on_notify)

        # -------------------------------
        # Handshake (STRICT)
        # -------------------------------
        await asyncio.sleep(0.2)
        await client.write_gatt_char(
            UART_RX_UUID,
            b"CLIENT_READY\n"
        )

        print("\nReady. Enter commands:")
        print("1 = Forward (one step)")
        print("2 = Backward (one step)")
        print("3 = Left (one step)")
        print("4 = Right (one step)")
        print("5 = Reset")
        print("6 = Stop\n")

        # -------------------------------
        # Command loop
        # -------------------------------
        while True:
            cmd = await asyncio.get_event_loop().run_in_executor(
                None, input, "> "
            )

            cmd = cmd.strip()
            if not cmd:
                continue

            # Send exactly what user typed
            await client.write_gatt_char(
                UART_RX_UUID,
                (cmd + "\n").encode()
            )

            await asyncio.sleep(0.05)


# ===============================
# ENTRY POINT
# ===============================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDisconnected")
