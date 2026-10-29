from machine import Pin, I2C
from time import sleep

print("Booting...")

i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=100000)
print("I2C initialized")

devices = i2c.scan()
print("I2C devices found:", devices)

while True:
    print("Alive")
    sleep(1)
