from time import sleep_ms
from core import state, servo

TRIPOD_A = [1,3,5]
TRIPOD_B = [2,4,6]

def step(tripod):
    lift = TRIPOD_A if tripod == "A" else TRIPOD_B
    push = TRIPOD_B if tripod == "A" else TRIPOD_A

    state.set_phase(state.PHASE_LIFT)
    for l in lift:
        servo.set_leg(l, servo.HIP_CENTER, servo.KNEE_UP)
        sleep_ms(40)

    state.set_phase(state.PHASE_SWING)
    for l in lift:
        servo.set_leg(l, servo.HIP_FORWARD, servo.KNEE_UP)
        sleep_ms(40)

    state.set_phase(state.PHASE_PUSH)
    for l in push:
        servo.set_leg(l, servo.HIP_BACKWARD, servo.KNEE_DOWN)
        sleep_ms(40)

    state.set_phase(state.PHASE_PLANT)
    for l in lift:
        servo.set_leg(l, servo.HIP_CENTER, servo.KNEE_DOWN)
        sleep_ms(40)

    return not state.abort_motion
