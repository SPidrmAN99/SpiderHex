from micropython import const
import bluetooth

_IRQ_CENTRAL_CONNECT    = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE        = const(3)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")

_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_NOTIFY,
)

_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_WRITE,
)

_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX))


def advertising_payload(name):
    return (
        b"\x02\x01\x06" +
        bytes((len(name) + 1, 0x09)) +
        name.encode()
    )


class BLEUART:
    def __init__(self, name="Spider-Hex"):
        print("BLE INIT")
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self._irq)

        ((self.tx, self.rx),) = self.ble.gatts_register_services(
            (_UART_SERVICE,)
        )

        self.connections = set()
        self._rx_buf = ""

        self._payload = advertising_payload(name)
        self.ble.gap_advertise(100, self._payload)
        print("BLE ADVERTISING AS:", name)

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn, _, _ = data
            self.connections.add(conn)

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn, _, _ = data
            self.connections.discard(conn)
            self.ble.gap_advertise(100, self._payload)

        elif event == _IRQ_GATTS_WRITE:
            msg = self.ble.gatts_read(self.rx).decode()
            self._rx_buf += msg

    def read_line(self):
        if "\n" not in self._rx_buf:
            return None
        line, self._rx_buf = self._rx_buf.split("\n", 1)
        return line.strip()

    def send(self, msg):
        data = (msg + "\n").encode()
        for c in self.connections:
            try:
                self.ble.gatts_notify(c, self.tx, data)
            except:
                pass
