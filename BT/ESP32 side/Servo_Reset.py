from machine import Pin, I2C
from time import sleep

# ========== CONFIG ==========
PCA9685_ADDR = 0x40
SERVO_MIN_ANGLE = 0
SERVO_MAX_ANGLE = 120   # safety limit

print("=== Servo Zero Program ===")

# ========== I2C INIT ==========
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
print("I2C initialized")

devices = i2c.scan()
print("I2C devices:", devices)

if PCA9685_ADDR not in devices:
    raise Exception("PCA9685 not found")

print("PCA9685 detected")

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
print("PWM frequency set to 50Hz")

# ========== SERVO HELPERS ==========
def angle_to_pulse(angle):
    angle = max(SERVO_MIN_ANGLE, min(SERVO_MAX_ANGLE, angle))
    return int(150 + (angle / 180) * 450)

def set_servo(channel, angle):
    pca.set_pwm(channel, angle_to_pulse(angle))
    sleep(0.5)

# ========== ZERO ALL SERVOS ==========
print("Setting all servos to 0°")

for ch in range(12):
    print(" Channel", ch, "→ 0°")
    set_servo(ch, 0)

print("All servos set to ZERO position")
print("Holding position...")

# ========== HOLD ==========
#while True:
    #sleep(1)