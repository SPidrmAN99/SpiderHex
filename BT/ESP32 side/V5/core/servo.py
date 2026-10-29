from machine import Pin, I2C
from time import sleep_ms
from core import state

PCA_ADDR = 0x40

HIP_CENTER   = 90
HIP_FORWARD  = 120
HIP_BACKWARD = 60
KNEE_UP      = 45
KNEE_DOWN    = 90

RIGHT_LEGS = [1, 2, 3]
LEFT_LEGS  = [4, 5, 6]

SERVOS = {
    1: {"hip": 0, "knee": 1},
    2: {"hip": 2, "knee": 3},
    3: {"hip": 4, "knee": 5},
    4: {"hip": 6, "knee": 7},
    5: {"hip": 8, "knee": 9},
    6: {"hip": 10,"knee":11},
}

class PCA9685:
    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(addr, 0x00, b"\x00")
        self.set_freq(50)

    def set_freq(self, hz):
        prescale = int(25000000 / (4096 * hz) - 1)
        self.i2c.writeto_mem(self.addr, 0x00, b"\x10")
        self.i2c.writeto_mem(self.addr, 0xFE, bytes([prescale]))
        self.i2c.writeto_mem(self.addr, 0x00, b"\x00")
        sleep_ms(5)
        self.i2c.writeto_mem(self.addr, 0x00, b"\xA1")

    def set_angle(self, ch, angle):
        pulse = int(102 + (angle / 180) * 410)
        reg = 0x06 + 4 * ch
        self.i2c.writeto_mem(
            self.addr,
            reg,
            bytes([0, 0, pulse & 0xFF, pulse >> 8])
        )


i2c = I2C(0, scl=Pin(22), sda=Pin(21))
pca = PCA9685(i2c, PCA_ADDR)


def set_leg(leg, hip, knee):
    if state.abort_motion:
        return

    if leg in RIGHT_LEGS:
        hip = 180 - hip

    pca.set_angle(SERVOS[leg]["hip"], hip)
    pca.set_angle(SERVOS[leg]["knee"], knee)
