# ===============================
# LEFT TURN (STEP-BASED)
# ===============================

from time import sleep_ms
from core import servo, state

# ---------- Tripod groups ----------
TRIPOD_A = [1, 3, 5]
TRIPOD_B = [2, 4, 6]

# ---------- Timing (ms) ----------
PHASE_DELAY = 40
STEP_PAUSE  = 120


def _lift(group):
    state.set_phase(state.PHASE_LIFT)
    for leg in group:
        servo.set_leg(leg, servo.HIP_CENTER, servo.KNEE_UP)
        sleep_ms(PHASE_DELAY)


def _swing(group):
    state.set_phase(state.PHASE_SWING)
    for leg in group:
        if leg in servo.LEFT_LEGS:
            servo.set_leg(leg, servo.HIP_BACKWARD, servo.KNEE_UP)
        else:
            servo.set_leg(leg, servo.HIP_FORWARD, servo.KNEE_UP)
        sleep_ms(PHASE_DELAY)


def _push(group):
    state.set_phase(state.PHASE_PUSH)
    for leg in group:
        if leg in servo.LEFT_LEGS:
            servo.set_leg(leg, servo.HIP_FORWARD, servo.KNEE_DOWN)
        else:
            servo.set_leg(leg, servo.HIP_BACKWARD, servo.KNEE_DOWN)
        sleep_ms(PHASE_DELAY)


def _plant(group):
    state.set_phase(state.PHASE_PLANT)
    for leg in group:
        servo.set_leg(leg, servo.HIP_CENTER, servo.KNEE_DOWN)
        sleep_ms(PHASE_DELAY)


# ===============================
# PUBLIC STEP API
# ===============================

def step(tripod):
    """
    Executes ONE left-turn tripod step.
    Returns False if aborted mid-step.
    """
    if state.abort_motion:
        return False

    if tripod == "A":
        lift, push = TRIPOD_A, TRIPOD_B
    else:
        lift, push = TRIPOD_B, TRIPOD_A

    _lift(lift)
    if state.abort_motion: return False

    _swing(lift)
    if state.abort_motion: return False

    _push(push)
    if state.abort_motion: return False

    _plant(lift)
    if state.abort_motion: return False

    sleep_ms(STEP_PAUSE)
    return True
