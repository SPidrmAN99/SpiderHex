from machine import Pin, I2C
from time import sleep

# ========== CONFIG ==========
PCA9685_ADDR = 0x40
CENTER_ANGLE = 90
WAVE_OFFSET  = 45        # +45° movement
DELAY        = 1         # seconds

print("=== Servo Wave Test Program ===")

# ========== I2C INIT ==========
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
devices = i2c.scan()
print("I2C devices:", devices)

if PCA9685_ADDR not in devices:
    raise Exception("PCA9685 not found")

# ========== PCA9685 ==========
class PCA9685:
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self.i2c.writeto_mem(self.address, 0x00, b'\x00')

    def set_freq(self, hz):
        prescale = int(25000000 / (4096 * hz) - 1)
        old = self.i2c.readfrom_mem(self.address, 0x00, 1)[0]
        self.i2c.writeto_mem(self.address, 0x00, bytes([(old & 0x7F) | 0x10]))
        self.i2c.writeto_mem(self.address, 0xFE, bytes([prescale]))
        self.i2c.writeto_mem(self.address, 0x00, bytes([old]))
        sleep(0.005)
        self.i2c.writeto_mem(self.address, 0x00, bytes([old | 0xA1]))

    def set_pwm(self, channel, pulse):
        pulse = max(0, min(4095, pulse))
        reg = 0x06 + 4 * channel
        self.i2c.writeto_mem(
            self.address,
            reg,
            bytearray([0, 0, pulse & 0xFF, pulse >> 8])
        )

pca = PCA9685(i2c, PCA9685_ADDR)
pca.set_freq(50)
print("PCA9685 ready @ 50Hz")

# ========== SERVO HELPERS ==========
def angle_to_pulse(angle):
    angle = max(0, min(180, angle))
    return int(150 + (angle / 180) * 450)

def set_servo(channel, angle):
    pca.set_pwm(channel, angle_to_pulse(angle))

# ========== CENTER ALL SERVOS ==========
print("Centering all servos (90°)")
for ch in range(16):
    set_servo(ch, CENTER_ANGLE)
    sleep(0.05)

sleep(1)
print("Starting wave motion")

# ========== WAVE TEST ==========
while True:
    for ch in range(16):
        print("Servo", ch, "→ +45°")
        set_servo(ch, CENTER_ANGLE + WAVE_OFFSET)
        sleep(DELAY)

        print("Servo", ch, "→ center")
        set_servo(ch, CENTER_ANGLE)
        sleep(0.2)
