from machine import Pin, time_pulse_us
import time
from core import state

TRIG = Pin(5, Pin.OUT)
ECHO = Pin(18, Pin.IN)

SAFE_DISTANCE_CM = 15
MAX_ECHO_US = 30000
MIN_ECHO_US = 150


def _read():
    TRIG.off()
    time.sleep_us(5)
    TRIG.on()
    time.sleep_us(10)
    TRIG.off()

    try:
        pulse = time_pulse_us(ECHO, 1, MAX_ECHO_US)
    except OSError:
        return None

    if pulse < MIN_ECHO_US or pulse > MAX_ECHO_US:
        return None

    return (pulse * 0.0343) / 2


def tick():
    dist = _read()
    state.distance_cm = dist
    state.forward_allowed = True

    if dist is not None and dist <= SAFE_DISTANCE_CM:
        state.forward_allowed = False
        if state.active_motion == state.FORWARD:
            state.request_abort(
                "Object too close ({:.1f} cm)".format(dist)
            )
