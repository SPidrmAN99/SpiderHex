from machine import Pin, I2C
from time import sleep

# ================= CONFIG =================
PCA_ADDR = 0x40

# SG90 SAFE ANGLES
HIP_CENTER   = 90
HIP_FORWARD  = 120
HIP_BACKWARD = 60
KNEE_UP      = 45
KNEE_DOWN    = 90

STEP_DELAY = 1

print("Booting HEXAPOD TRIPOD WALK PROGRAM")

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

# ================= SERVO MAP =================
# leg : hip, knee
servos = {
    1: {"hip": 0,  "knee": 1},
    2: {"hip": 2,  "knee": 3},
    3: {"hip": 4,  "knee": 5},
    4: {"hip": 6,  "knee": 7},
    5: {"hip": 8,  "knee": 9},
    6: {"hip": 10, "knee": 11}
}

TRIPOD_A = [1, 3, 5]
TRIPOD_B = [2, 4, 6]

# ================= SERVO HELPERS =================
def angle_to_pulse(angle):
    angle = max(0, min(180, angle))
    return int(150 + (angle / 180) * 450)

def set_servo(ch, angle):
    pca.set_pwm(ch, angle_to_pulse(angle))

def set_leg(leg, hip, knee):
    set_servo(servos[leg]["hip"], hip)
    set_servo(servos[leg]["knee"], knee)

# ================= POSTURES =================
def stand():
    print("Standing posture")
    for leg in servos:
        set_leg(leg, HIP_CENTER, KNEE_DOWN)
        sleep(0.05)

def lift_tripod(tripod):
    for leg in tripod:
        set_leg(leg, HIP_CENTER, KNEE_UP)

def swing_tripod(tripod, direction):
    for leg in tripod:
        set_leg(leg, direction, KNEE_UP)

def plant_tripod(tripod, direction):
    for leg in tripod:
        set_leg(leg, direction, KNEE_DOWN)

# ================= WALK STEP =================
def tripod_step(tripod_lift, tripod_push):
    print(" Lifting:", tripod_lift)
    lift_tripod(tripod_lift)
    sleep(STEP_DELAY)

    print(" Swinging lifted legs forward")
    swing_tripod(tripod_lift, HIP_FORWARD)

    print(" Pushing body forward with:", tripod_push)
    for leg in tripod_push:
        set_leg(leg, HIP_BACKWARD, KNEE_DOWN)

    sleep(STEP_DELAY)

    print(" Planting lifted legs")
    plant_tripod(tripod_lift, HIP_FORWARD)
    sleep(STEP_DELAY)

# ================= WALK =================
def walk(steps):
    print("Walking forward | steps:", steps)
    for i in range(steps):
        print("Step", i + 1, "— Tripod A")
        tripod_step(TRIPOD_A, TRIPOD_B)
        sleep(1)
        
        print("Step", i + 1, "— Tripod B")
        tripod_step(TRIPOD_B, TRIPOD_A)

# ================= MAIN =================
sleep(1)
stand()
sleep(1)

walk(2)

print("Walk complete. Holding position.")
'''while True:
    #walk(1)
    sleep(1)
    #sleep(1)
'''