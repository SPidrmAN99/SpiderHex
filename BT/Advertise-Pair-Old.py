from micropython import const
import bluetooth
import struct
import time

# IRQ events
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

# Nordic UART Service (NUS) UUIDs
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
            bluetooth.FLAG_NOTIFY | bluetooth.FLAG_READ)
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
            bluetooth.FLAG_WRITE)

_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX))

def advertising_payload(name):
    return (
        b'\x02\x01\x06' +
        bytes((len(name) + 1, 0x09)) + name.encode()
    )

class BLEUART:
    def __init__(self, ble, name="Spider-Hex"):
        self.ble = ble
        self.ble.active(True)
        self.ble.irq(self.irq)

        ((self.tx, self.rx),) = self.ble.gatts_register_services((_UART_SERVICE,))
        self.connections = set()

        self.ble.gap_advertise(100, advertising_payload(name))
        print("Advertising as", name)

    def irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self.connections.add(conn_handle)
            print("Connected")

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self.connections.discard(conn_handle)
            print("Disconnected")
            self.ble.gap_advertise(100, advertising_payload("Spider-Hex"))

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self.rx:
                msg = self.ble.gatts_read(self.rx)
                try:
                    text = msg.decode().strip()
                    print("RX:", text)
                    self.send(b"ACK: " + msg + b"\n")
                except:
                    pass

    def send(self, data):
        for conn_handle in self.connections:
            self.ble.gatts_notify(conn_handle, self.tx, data)

ble = bluetooth.BLE()
uart = BLEUART(ble)

while True:
    #uart.send(b"Hello from ESP32\n")
    time.sleep(1)

