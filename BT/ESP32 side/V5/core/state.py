IDLE     = "IDLE"
FORWARD  = "FORWARD"
BACKWARD = "BACKWARD"
LEFT     = "LEFT"
RIGHT    = "RIGHT"
RESET    = "RESET"

PHASE_NONE  = "NONE"
PHASE_LIFT  = "LIFT"
PHASE_SWING = "SWING"
PHASE_PUSH  = "PUSH"
PHASE_PLANT = "PLANT"
PHASE_RESET = "RESET"

active_motion = IDLE
active_phase  = PHASE_NONE
busy = False

abort_motion = False
abort_reason = None

distance_cm = None
forward_allowed = True

client_ready = False
tick = 0


def enter_motion(motion):
    global active_motion, busy, abort_motion, abort_reason
    active_motion = motion
    busy = True
    abort_motion = False
    abort_reason = None


def exit_motion():
    global active_motion, active_phase, busy, abort_motion, abort_reason
    active_motion = IDLE
    active_phase = PHASE_NONE
    busy = False
    abort_motion = False
    abort_reason = None


def set_phase(phase):
    global active_phase, tick
    active_phase = phase
    tick += 1


def request_abort(reason):
    global abort_motion, abort_reason
    abort_motion = True
    abort_reason = reason
