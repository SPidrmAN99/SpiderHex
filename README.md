# SpiderHex

MicroPython and BLE control code for a six-legged Spider-Hex robot.

## Repository layout

- `BT/ESP32 side/` contains ESP32 MicroPython BLE server and motion code. The root files are earlier iterations; `V5/` is an experimental modular prototype copied from the project archive.
- `BT/Laptop side/` contains Python BLE clients. The `V5/` client pairs with the V5 ESP32 prototype.
- `Control_Logic/` contains gait and control reference documents.

## V5 prototype

The V5 snapshot is included for development and comparison. It has not been validated on the robot. In particular, its motion loop runs synchronously and does not process BLE commands or refresh the ultrasonic distance reading while a gait step is executing. Treat the `STOP` command and obstacle abort as unverified; do not rely on them as safety controls.

The firmware expects MicroPython on an ESP32, a PCA9685 servo controller at I2C address `0x40` (SDA 21, SCL 22), and an HC-SR04-style sensor (TRIG 5, ECHO 18). Servo angles and wiring may need adjustment for the assembled robot.

The laptop client uses Python with `bleak`. It scans for the BLE device named `Spider-Hex`; the firmware and client exchange newline-terminated commands over the Nordic UART service.

## Commands

The V5 client sends `1` forward, `2` backward, `3` left, `4` right, `5` reset, and `6` stop. These commands are still experimental.

## Project gallery

### Robot prototype

<img src="docs/images/assembled-spiderhex-prototype.png" alt="Assembled Spider-Hex prototype with ESP32 and servo wiring" width="420">

<img src="docs/images/team-engraved-top-plate.png" alt="Engraved Spider-Hex top plate" width="420">

### CAD design

<img src="docs/images/leg-gearbox-cad-render.png" alt="CAD render of the Spider-Hex leg gearbox and linkage" width="520">

<img src="docs/images/leg-joint-cad-render.png" alt="CAD render of a Spider-Hex leg joint and gear" width="520">

### Mobile controller

These screenshots show the Android controller connecting over BLE and issuing movement and servo-reset commands.

<img src="docs/images/mobile-controller-ble-connected.jpg" alt="Mobile app showing a successful BLE connection and motion controls" width="260">

<img src="docs/images/mobile-controller-left-turn.jpg" alt="Mobile app issuing a left-turn command" width="260">

<img src="docs/images/mobile-controller-servo-reset.jpg" alt="Mobile app issuing a servo-reset command" width="260">
