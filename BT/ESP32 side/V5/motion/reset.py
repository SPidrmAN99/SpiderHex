# ===============================
# RESET / NEUTRAL POSE
# ===============================

from time import sleep_ms
from core import servo, state

PHASE_DELAY = 40


def step():
    """
    Moves all legs to neutral position once.
    Returns False if aborted.
    """
    state.set_phase(state.PHASE_RESET)

    for leg in servo.SERVOS:
        if state.abort_motion:
            return False

        servo.set_leg(
            leg,
            servo.HIP_CENTER,
            servo.KNEE_DOWN
        )
        sleep_ms(PHASE_DELAY)

    return True
