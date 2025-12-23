import gc

# Map choices to script filenames
SCRIPTS = {
    1: "Forward.py",
    2: "Backward.py",
    3: "Left_Turn.py",
    4: "Right_Turn.py",
    5: "Servo_Reset.py"
}

def run_script(filename):
    print("\nExecuting:", filename)
    print("-" * 30)
    try:
        with open(filename) as f:
            exec(f.read(), {})  # Execute script in isolated namespace
    except Exception as e:
        print("Runtime error:", e)
    gc.collect()

def menu():
    while True:
        print("\n===== MOTION CONTROL MENU =====")
        print("1 = Forward")
        print("2 = Backward")
        print("3 = Left Turn")
        print("4 = Right Turn")
        print("5 = Servo Reset")
        print("6 = Exit")

        try:
            choice = int(input("> "))
        except:
            print("Invalid input")
            continue

        if choice == 6:
            print("\nTerminating menu. System idle.")
            break  # exit the menu loop safely

        if choice in SCRIPTS:
            run_script(SCRIPTS[choice])
        else:
            print("Invalid selection")
