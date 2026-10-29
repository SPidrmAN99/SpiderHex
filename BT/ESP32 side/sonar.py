from machine import Pin, time_pulse_us
import time

TRIG = Pin(5, Pin.OUT)
ECHO = Pin(18, Pin.IN)

def get_distance():
    # Clean trigger
    TRIG.value(0)
    time.sleep_us(5)

    # 10us pulse
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)

    try:
        pulse = time_pulse_us(ECHO, 1, 30000)  # 30ms timeout
    except OSError:
        return None

    if pulse <= 0:
        return None

    # Distance in cm
    return (pulse * 0.0343) / 2


while True:
    dist = get_distance()

    if dist is None:
        print("No object detected")
    else:
        if dist < 15:
            print("⚠️ WARNING: Obstacle too close! Distance: {:.1f} cm".format(dist))

        else:
            print("Distance: {:.1f} cm".format(dist))

    time.sleep(0.3)
