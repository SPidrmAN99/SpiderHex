from machine import Pin, time_pulse_us
import time

# ---------------- SENSOR SETUP ----------------
TRIG = Pin(5, Pin.OUT)
ECHO = Pin(18, Pin.IN)

SAFE_DISTANCE = 25  # cm

# ---------------- SERVO ANGLES ----------------
HIP_CENTER   = 90
HIP_FORWARD  = 130
HIP_BACKWARD = 50

KNEE_UP   = 40
KNEE_DOWN = 90

# ---------------- TRIPOD GROUPS ----------------
TRIPOD_A = [1, 3, 5]
TRIPOD_B = [2, 4, 6]

# ---------------- STATES ----------------
STATE_FORWARD    = 0
STATE_BACKWARD   = 1
STATE_TURN_RIGHT = 2

state = STATE_FORWARD

# ---------------- DISTANCE FUNCTION ----------------
def get_distance():
    TRIG.off()
    time.sleep_us(2)

    TRIG.on()
    time.sleep_us(10)
    TRIG.off()

    duration = time_pulse_us(ECHO, 1, 30000)

    if duration < 0:
        return None

    distance = (duration * 0.0343) / 2
    return distance

# ---------------- SERVO PLACEHOLDERS ----------------
def set_hip(leg, angle):
    pass  # PCA9685 hip control goes here

def set_knee(leg, angle):
    pass  # PCA9685 knee control goes here

# ---------------- TRIPOD MOVEMENT ----------------
def move_tripod(tripod, hip_angle):
    for leg in tripod:
        set_knee(leg, KNEE_UP)
        set_hip(leg, hip_angle)

    time.sleep(0.2)

    for leg in tripod:
        set_knee(leg, KNEE_DOWN)

    time.sleep(0.2)

# ---------------- WALKING FUNCTIONS ----------------
def walk_forward():
    move_tripod(TRIPOD_A, HIP_FORWARD)
    move_tripod(TRIPOD_B, HIP_FORWARD)

def walk_backward(steps=1):
    for _ in range(steps):
        move_tripod(TRIPOD_A, HIP_BACKWARD)
        move_tripod(TRIPOD_B, HIP_BACKWARD)

def turn_right():
    move_tripod([1, 5, 6], HIP_FORWARD)
    move_tripod([2, 3, 4], HIP_BACKWARD)

# ---------------- MAIN LOOP ----------------
while True:
    distance = get_distance()

    if distance is not None and distance <= SAFE_DISTANCE:
        state = STATE_BACKWARD

    if state == STATE_FORWARD:
        walk_forward()

    elif state == STATE_BACKWARD:
        walk_backward(2)
        state = STATE_TURN_RIGHT

    elif state == STATE_TURN_RIGHT:
        turn_right()
        state = STATE_FORWARD


