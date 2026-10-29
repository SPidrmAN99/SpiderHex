from machine import I2C, Pin
import time

# ================= CONFIGURATION =================
HIP_CENTER   = 90
HIP_FORWARD  = 120
HIP_BACKWARD = 60

KNEE_UP      = 45
KNEE_DOWN    = 90

PCA_ADDR = 0x40
I2C_SCL  = 22
I2C_SDA  = 21

RIGHT_LEGS = [1, 2, 3]

TRIPOD_A = [1, 3, 5]
TRIPOD_B = [2, 4, 6]

SERVOS = {
    1: {"hip": 0,  "knee": 1},
    2: {"hip": 2,  "knee": 3},
    3: {"hip": 4,  "knee": 5},
    4: {"hip": 6,  "knee": 7},
    5: {"hip": 8,  "knee": 9},
    6: {"hip": 10, "knee": 11}
}

# ================= I2C / PCA9685 =================
i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=100000)

class PCA9685:
    def __init__(self, i2c, address=0x40):
        self.i2c = i2c
        self.address = address
        self.reset()
        self.set_freq(50)

    def reset(self):
        self.i2c.writeto_mem(self.address, 0x00, b'\x00')
        time.sleep(0.01)

    def set_freq(self, freq):
        prescale = int(25000000 / (4096 * freq) - 1)
        old = self.i2c.readfrom_mem(self.address, 0x00, 1)[0]
        self.i2c.writeto_mem(self.address, 0x00, bytes([(old & 0x7F) | 0x10]))
        self.i2c.writeto_mem(self.address, 0xFE, bytes([prescale]))
        self.i2c.writeto_mem(self.address, 0x00, bytes([old | 0xA1]))
        time.sleep(0.005)

    def set_pwm(self, channel, on, off):
        data = bytearray(4)
        data[0] = on & 0xFF
        data[1] = on >> 8
        data[2] = off & 0xFF
        data[3] = off >> 8
        self.i2c.writeto_mem(self.address, 0x06 + 4 * channel, data)

    def set_angle(self, channel, angle):
        angle = max(0, min(180, angle))
        pulse = int(102 + (angle / 180) * 410)
        self.set_pwm(channel, 0, pulse)

pca = PCA9685(i2c)

# ================= STATE MEMORY =================
current_state = {
    leg: {"hip": HIP_CENTER, "knee": KNEE_DOWN}
    for leg in SERVOS
}

# ================= LOW LEVEL =================
def write_leg(leg, hip, knee):
    current_state[leg]["hip"] = hip
    current_state[leg]["knee"] = knee

    if leg in RIGHT_LEGS:
        hip = 180 - hip

    pca.set_angle(SERVOS[leg]["hip"], hip)
    pca.set_angle(SERVOS[leg]["knee"], knee)

def move_leg_smooth(leg, hip=None, knee=None, steps=6, delay=0.02):
    h0 = current_state[leg]["hip"]
    k0 = current_state[leg]["knee"]

    h1 = h0 if hip is None else hip
    k1 = k0 if knee is None else knee

    dh = (h1 - h0) / steps
    dk = (k1 - k0) / steps

    h = h0
    k = k0

    for _ in range(steps):
        h += dh
        k += dk
        write_leg(leg, int(h), int(k))
        time.sleep(delay)

def move_group_sync(targets, steps=8, delay=0.015):
    inc = {}
    for leg, t in targets.items():
        h0 = current_state[leg]["hip"]
        k0 = current_state[leg]["knee"]
        inc[leg] = {
            "h": h0,
            "k": k0,
            "dh": (t["hip"] - h0) / steps,
            "dk": (t["knee"] - k0) / steps
        }

    for _ in range(steps):
        for leg in inc:
            inc[leg]["h"] += inc[leg]["dh"]
            inc[leg]["k"] += inc[leg]["dk"]
            write_leg(
                leg,
                int(inc[leg]["h"]),
                int(inc[leg]["k"])
            )
        time.sleep(delay)

# ================= POWER SAFE GAIT =================
def lift_tripod_sequential(tripod):
    for leg in tripod:
        move_leg_smooth(leg, knee=KNEE_UP)
        time.sleep(0.3)

def swing_tripod_sequential(tripod):
    for leg in tripod:
        move_leg_smooth(leg, hip=HIP_FORWARD)
        time.sleep(0.3)

def lower_tripod_sequential(tripod):
    for leg in tripod:
        move_leg_smooth(leg, knee=KNEE_DOWN)
        time.sleep(0.3)

def push_tripod_sync(tripod):
    targets = {
        leg: {"hip": HIP_BACKWARD, "knee": KNEE_DOWN}
        for leg in tripod
    }
    move_group_sync(targets)
    time.sleep(0.5)

def forward_step(lift_group, push_group):
    lift_tripod_sequential(lift_group)
    swing_tripod_sequential(lift_group)
    push_tripod_sync(push_group)
    lower_tripod_sequential(lift_group)

# ================= STAND =================
def stand():
    targets = {
        leg: {"hip": HIP_CENTER, "knee": KNEE_DOWN}
        for leg in SERVOS
    }
    move_group_sync(targets, steps=15, delay=0.02)

# ================= MAIN =================
print("Robot Active")
stand()
time.sleep(1)

for _ in range(4):
    forward_step(TRIPOD_A, TRIPOD_B)
    time.sleep(0.5)
    forward_step(TRIPOD_B, TRIPOD_A)
    time.sleep(0.5)

stand()
print("Done")
