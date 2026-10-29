from machine import Pin, I2C
from time import sleep, ticks_ms, ticks_diff

# ========== CONFIG ==========
PCA9685_ADDR = 0x40
ch = 1

SERVO_MIN_ANGLE = 0
SERVO_MAX_ANGLE = 300
S_ANGLE = 80
SERVO_RESET_ANGLE = S_ANGLE - 30     # neutral / center

PWM_FREQ = 50              # standard servo
MOVE_TIME_MS = 2000         # time taken to reset EACH servo (ms)

TOTAL_CHANNELS = 12

print("=== Smooth Servo Reset Program ===")

# ========== I2C INIT ==========
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
devices = i2c.scan()
print("I2C devices:", devices)

if PCA9685_ADDR not in devices:
    raise RuntimeError("PCA9685 not found")

print("PCA9685 detected")

# ========== PCA9685 DRIVER ==========
class PCA9685:
    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(self.addr, 0x00, b'\x00')

    def set_freq(self, hz):
        prescale = int(25000000 / (4096 * hz) - 1)
        old = self.i2c.readfrom_mem(self.addr, 0x00, 1)[0]
        self.i2c.writeto_mem(self.addr, 0x00, bytes([(old & 0x7F) | 0x10]))
        self.i2c.writeto_mem(self.addr, 0xFE, bytes([prescale]))
        self.i2c.writeto_mem(self.addr, 0x00, bytes([old]))
        sleep(0.005)
        self.i2c.writeto_mem(self.addr, 0x00, bytes([old | 0xA1]))

    def set_pwm(self, ch, pulse):
        pulse = max(0, min(4095, pulse))
        reg = 0x06 + 4 * ch
        self.i2c.writeto_mem(
            self.addr,
            reg,
            bytearray([0, 0, pulse & 0xFF, pulse >> 8])
        )

pca = PCA9685(i2c, PCA9685_ADDR)
pca.set_freq(PWM_FREQ)
print("PWM frequency set to 50Hz")

# ========== SERVO MATH ==========
def angle_to_pulse(angle):
    angle = max(SERVO_MIN_ANGLE, min(SERVO_MAX_ANGLE, angle))
    return int(150 + (angle / 180) * 450)

# ========== SMOOTH MOTION ENGINE ==========
def move_servo_smooth(channel, start_angle, end_angle, duration_ms):
    start_time = ticks_ms()
    end_time = start_time + duration_ms

    while True:
        now = ticks_ms()
        if ticks_diff(now, end_time) >= 0:
            break

        t = ticks_diff(now, start_time) / duration_ms
        angle = start_angle + (end_angle - start_angle) * t

        pca.set_pwm(channel, angle_to_pulse(angle))
        sleep(0.02)  # ~50Hz update

    pca.set_pwm(channel, angle_to_pulse(end_angle))

# ========== RESET ALL SERVOS (SMOOTH) ==========
print("Resetting all servos smoothly to", SERVO_RESET_ANGLE, "degrees")

for ch in TOTAL_CHANNELS:
    print(" Channel", ch, "→", SERVO_RESET_ANGLE, "° (smooth)")

    # Assumption: worst-case unknown start, approach safely from mid-range
    move_servo_smooth(
        channel=ch,
        start_angle=S_ANGLE,
        end_angle=SERVO_RESET_ANGLE,
        duration_ms=MOVE_TIME_MS
    )

    sleep(0.3)   # small gap between channels

print("All servos reset smoothly")
print("Holding position...")
