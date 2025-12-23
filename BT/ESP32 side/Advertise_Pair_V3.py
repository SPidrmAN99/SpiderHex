from micropython import const
import bluetooth

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
            bluetooth.FLAG_NOTIFY)
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
            bluetooth.FLAG_WRITE)

_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX))


def advertising_payload(name):
    return (
        b"\x02\x01\x06" +
        bytes((len(name) + 1, 0x09)) + name.encode()
    )


class BLEUART:
    def __init__(self, ble, name="Spider-Hex"):
        self.ble = ble
        self.ble.active(True)
        self.ble.irq(self._irq)

        ((self.tx, self.rx),) = self.ble.gatts_register_services((_UART_SERVICE,))
        self.connections = set()
        self.rx_buffer = ""

        self.ble.gap_advertise(100, advertising_payload(name))
        print("Advertising as", name)

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn, _, _ = data
            self.connections.add(conn)
            print("BLE Connected")

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn, _, _ = data
            self.connections.discard(conn)
            print("BLE Disconnected")
            self.ble.gap_advertise(100, advertising_payload("Spider-Hex"))

        elif event == _IRQ_GATTS_WRITE:
            data = self.ble.gatts_read(self.rx).decode()
            self.rx_buffer += data

    def send(self, msg):
        for conn in self.connections:
            self.ble.gatts_notify(conn, self.tx, msg + "\n")

    def read(self):
        if "\n" not in self.rx_buffer:
            return None
        line, self.rx_buffer = self.rx_buffer.split("\n", 1)
        return line.strip()

    def is_connected(self):
        return bool(self.connections)
