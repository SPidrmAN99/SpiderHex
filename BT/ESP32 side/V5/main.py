from time import sleep_ms
from core import state, ble, sonar
from motion import forward, backward, left, right, reset

uart = ble.BLEUART()

uart.send("BOOTING...")


def send_ready():
    uart.send(
        "SERVER READY | DIST={} | MENU: "
        "1 FWD 2 BACK 3 LEFT 4 RIGHT 5 RESET 6 STOP"
        .format(state.distance_cm)
    )


def handle_command(cmd):
    if not state.client_ready:
        if cmd == "CLIENT_READY":
            state.client_ready = True
            send_ready()
        return

    if state.busy:
        uart.send("BLOCKED: {}".format(state.active_motion))
        return

    if cmd == "1" and state.forward_allowed:
        state.enter_motion(state.FORWARD)
    elif cmd == "2":
        state.enter_motion(state.BACKWARD)
    elif cmd == "3":
        state.enter_motion(state.LEFT)
    elif cmd == "4":
        state.enter_motion(state.RIGHT)
    elif cmd == "5":
        state.enter_motion(state.RESET)
    elif cmd == "6":
        state.exit_motion()
    else:
        uart.send("INVALID / BLOCKED")


def execute_motion():
    tripod = "A"
    while state.busy and not state.abort_motion:
        ok = {
            state.FORWARD: forward.step,
            state.BACKWARD: backward.step,
            state.LEFT: left.step,
            state.RIGHT: right.step,
        }.get(state.active_motion, lambda _: False)(tripod)

        if not ok:
            break

        uart.send(
            "PHASE={} | DIST={}".format(
                state.active_phase, state.distance_cm
            )
        )
        tripod = "B" if tripod == "A" else "A"

    if state.abort_motion:
        uart.send("ABORTED: {}".format(state.abort_reason))

    state.exit_motion()
    send_ready()


while True:
    sonar.tick()

    cmd = uart.read_line()
    if cmd:
        handle_command(cmd)

    if state.busy:
        execute_motion()

    sleep_ms(20)
