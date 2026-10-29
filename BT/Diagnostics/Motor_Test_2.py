from machine import Pin, I2C
from time import sleep

# ================= CONFIG =================
PCA_ADDR = 0x40

CENTER_ANGLE = 0
MOVE_OFFSET  = 120
wait_time = 0

print("Booting SINGLE SERVO TEST (CH1)")

# ================= I2C =================
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
devices = i2c.scan()
print("I2C devices:", devices)

if PCA_ADDR not in devices:
    raise Exception("PCA9685 not found")

# ================= PCA9685 =================
class PCA9685:
    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr
        # Reset only once
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

pca = PCA9685(i2c, PCA_ADDR)
pca.set_freq(50)
print("PCA9685 ready @ 50Hz")

# ================= SERVO HELPERS =================
def angle_to_pulse(angle):
    angle = max(0, min(180, angle))
    return int(150 + (angle / 180) * 450)

def set_servo(channel, angle):
    pca.set_pwm(channel, angle_to_pulse(angle))

# ================= SINGLE SERVO LOOP =================
print("Driving ONLY servo channel 1")

# Initial center (ONLY CH1)
#set_servo(1, CENTER_ANGLE)
#set_servo(2, CENTER_ANGLE)
for i in range(0, 12):
    set_servo(i, CENTER_ANGLE)
    sleep(wait_time)
sleep(1)

while True:
    #for i in range 10
    print("Servo 1 → +45°")
    for i in range(0, 12):
        set_servo(i, CENTER_ANGLE + MOVE_OFFSET)
        sleep(wait_time)
    #set_servo(1, CENTER_ANGLE + MOVE_OFFSET)
    #set_servo(2, CENTER_ANGLE + MOVE_OFFSET)
    sleep(1)

    print("Servo 1 → center")
    for i in range(0, 13):
        set_servo(i, CENTER_ANGLE)
        sleep(wait_time)
    #set_servo(1, CENTER_ANGLE)
    #set_servo(2, CENTER_ANGLE)
    sleep(1)

    #return False
