import gc

SCRIPTS = {
    "1": "Forward.py",
    "2": "Backward.py",
    "3": "Left_Turn.py",
    "4": "Right_Turn.py",
    "5": "Servo_Reset.py",
}


def show_menu(send):
    send("===== MOTION CONTROL MENU =====")
    send("1 = Forward")
    send("2 = Backward")
    send("3 = Left Turn")
    send("4 = Right Turn")
    send("5 = Servo Reset")
    send("6 = Exit (idle)")
    send("m = Show menu again")
    send("Enter choice:")


def run_script(filename, send):
    send("SERVER_BUSY")
    send("Executing: " + filename)

    def ble_print(*args):
        send(" ".join(str(a) for a in args))

    try:
        with open(filename) as f:
            exec(f.read(), {"print": ble_print})
        send("Done.")
    except Exception as e:
        send("Runtime error: " + str(e))
    finally:
        gc.collect()
        send("SERVER_IDLE")


def handle_choice(choice, send):
    choice = choice.lower()

    if choice == "m":
        show_menu(send)
        send("SERVER_IDLE")
        return

    if choice == "6":
        send("Menu idle. Send 'm' to show menu.")
        send("SERVER_IDLE")
        return

    if choice in SCRIPTS:
        run_script(SCRIPTS[choice], send)
        show_menu(send)
    else:
        send("Invalid selection")
        show_menu(send)
        send("SERVER_IDLE")
