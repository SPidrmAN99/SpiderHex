from machine import I2C, Pin, time_pulse_us
import time

# ================= CONFIGURATION =================
HIP_CENTER   = 90
HIP_FORWARD  = 120     # Push forward
HIP_BACKWARD = 60      # Push backward

KNEE_UP      = 45
KNEE_DOWN    = 90

PCA_ADDR = 0x40
I2C_SCL  = 22
I2C_SDA  = 21

RIGHT_LEGS = [1, 2, 3]
LEFT_LEGS  = [4, 5, 6]

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

# ================= SONAR / HC-SR04 =================
TRIG = Pin(5, Pin.OUT)
ECHO = Pin(18, Pin.IN)

def get_distance():
    # Ensure trigger is LOW
    TRIG.off()
    time.sleep_us(2)

    # Send 10us pulse
    TRIG.on()
    time.sleep_us(10)
    TRIG.off()

    # Measure echo pulse width
    pulse_time = time_pulse_us(ECHO, 1, 30000)  # timeout = 30ms

    if pulse_time < 0:
        return None  # No echo received

    # Convert time to distance (cm)
    distance = (pulse_time * 0.0343) / 2
    return distance

obstacle_distance = get_distance()

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
        pulse = int(120 + (angle / 180) * 360)
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

def lerp(a, b, t):
    return a + (b - a) * t

def move_leg_smooth(leg, hip=None, knee=None, duration=500):
    h0 = current_state[leg]["hip"]
    k0 = current_state[leg]["knee"]

    h1 = h0 if hip is None else hip
    k1 = k0 if knee is None else knee

    start = time.ticks_ms()
    end = start + duration

    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now, end) >= 0:
            break

        t = time.ticks_diff(now, start) / duration
        write_leg(
            leg,
            int(lerp(h0, h1, t)),
            int(lerp(k0, k1, t))
        )
        time.sleep(0.02)   # ~50 Hz, same as backward.py

    write_leg(leg, h1, k1)

def move_group_sync(targets, duration=400):
    start = time.ticks_ms()
    end = start + duration

    start_state = {
        leg: {
            "hip": current_state[leg]["hip"],
            "knee": current_state[leg]["knee"]
        }
        for leg in targets
    }

    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now, end) >= 0:
            break

        t = time.ticks_diff(now, start) / duration

        for leg, target in targets.items():
            h = lerp(start_state[leg]["hip"], target["hip"], t)
            k = lerp(start_state[leg]["knee"], target["knee"], t)
            write_leg(leg, int(h), int(k))

        time.sleep(0.02)

    for leg, target in targets.items():
        write_leg(leg, target["hip"], target["knee"])

# ================= POWER SAFE =================
def lift_tripod_sequential(tripod):
    for leg in tripod:
        move_leg_smooth(leg, knee=KNEE_UP)
        time.sleep(0.3)

def lower_tripod_sequential(tripod):
    for leg in tripod:
        move_leg_smooth(leg, knee=KNEE_DOWN)
        time.sleep(0.3)

# ================= LEFT ROTATION STEP =================
def left_step(lift_group, push_group):
    # 1. Lift air legs
    obstacle_distance = get_distance()
    print("Distance from obstacle: ", obstacle_distance, 'cm')
    lift_tripod_sequential(lift_group)

    # 2. Swing lifted legs for rotation
    obstacle_distance = get_distance()
    print("Distance from obstacle: ", obstacle_distance, 'cm')
    for leg in lift_group:
        if leg in LEFT_LEGS:
            move_leg_smooth(leg, hip=HIP_BACKWARD)
        else:
            move_leg_smooth(leg, hip=HIP_FORWARD)
        time.sleep(0.3)

    # 3. Push ground legs opposite
    obstacle_distance = get_distance()
    print("Distance from obstacle: ", obstacle_distance, 'cm')
    targets = {}
    for leg in push_group:
        if leg in LEFT_LEGS:
            targets[leg] = {"hip": HIP_FORWARD, "knee": KNEE_DOWN}
        else:
            targets[leg] = {"hip": HIP_BACKWARD, "knee": KNEE_DOWN}

    move_group_sync(targets)
    time.sleep(0.5)

    # 4. Lower air legs
    obstacle_distance = get_distance()
    print("Distance from obstacle: ", obstacle_distance, 'cm')
    lower_tripod_sequential(lift_group)

# ================= STAND =================
def stand():
    targets = {
        leg: {"hip": HIP_CENTER, "knee": KNEE_DOWN}
        for leg in SERVOS
    }
    move_group_sync(targets, duration=800)

# ================= MAIN =================
print("Left Rotation Active")
stand()
time.sleep(1)

for _ in range(1):
    left_step(TRIPOD_A, TRIPOD_B)
    time.sleep(0.5)
    left_step(TRIPOD_B, TRIPOD_A)
    time.sleep(0.5)

stand()
print("Left Rotation Done")
