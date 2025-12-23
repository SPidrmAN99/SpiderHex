import gc

SCRIPTS = {
    "1": "Forward.py",
    "2": "Backward.py",
    "3": "Left_Turn.py",
    "4": "Right_Turn.py",
    "5": "Servo_Reset.py"
}


def show_menu(send):
    send("")
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


def handle_choice(choice, send):
    if choice.lower() == "m":
        show_menu(send)
        return True

    if choice == "6":
        send("Menu idle. Send 'm' to show menu.")
        return True

    if choice in SCRIPTS:
        run_script(SCRIPTS[choice], send)
    else:
        send("Invalid selection")

    return True
