from machine import I2C, Pin
import time
import ustruct

# ---------------- PCA9685 SETUP ----------------
i2c = I2C(0, sda=Pin(21), scl=Pin(22))
address = 0x40

# Reset PCA9685
i2c.writeto_mem(address, 0x00, b'\x00')

# Set frequency to 50 Hz
freq = 50
prescale = int(25000000 / (4096 * freq) - 1)
old = i2c.readfrom_mem(address, 0x00, 1)[0]
i2c.writeto_mem(address, 0x00, bytes([(old & 0x7F) | 0x10]))
i2c.writeto_mem(address, 0xFE, bytes([prescale]))
i2c.writeto_mem(address, 0x00, bytes([old]))
time.sleep_ms(5)
i2c.writeto_mem(address, 0x00, bytes([old | 0xA1]))

# ---------------- HELPER FUNCTION ----------------
def set_servo(ch, angle):
    # Convert angle to pulse (for SG90)
    pulse = int(150 + (angle / 180) * 450)
    data = ustruct.pack('<HH', 0, pulse)
    i2c.writeto_mem(address, 0x06 + 4 * ch, data)

# ---------------- SERVOS ----------------
servos = [1, 3, 5, 6]  # your 4 servos

# ---------------- TEST LOOP ----------------
while True:
    for angle in [0, 45, 90, 45]:
        print("Moving servos to", angle, "degrees")
        for s in servos:
            set_servo(s, angle)
        time.sleep(2)
