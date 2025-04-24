# 🤖 Afrobotics: African Robotics Learning Platform

_A modular, AI-enabled, person-following robot with a robotic arm, built for secondary and technical school students across Africa._

---

## 📦 Project Overview

**Afrobotics** is an open-source robotics education initiative designed to teach real-world robotics, computer vision, and control systems using **accessible hardware** and a **hands-on curriculum**.

Students will build a mobile robot powered by a **Raspberry Pi**, a **Bluetooth Xbox controller**, and a **3-DOF robotic arm**, capable of **tracking and interacting** with the environment using an onboard camera and AI.

> 🔧 Designed for classrooms, clubs, and community STEM programs.

---

## 🎯 Learning Outcomes

By completing this project, students will:

- Wire and program a robot using a Raspberry Pi
- Understand motor control and power distribution
- Use computer vision to track and follow people
- Build and operate a 3DOF robotic arm
- Control the robot wirelessly with an Xbox controller
- Design and compete in field-based robotics challenges

---

## 📚 Curriculum Modules

| Module | Title                          | Description                                 |
|--------|--------------------------------|---------------------------------------------|
| 00     | 📘 Project Introduction         | Goals, setup, and hardware overview         |
| 01     | 📷 Camera + Raspberry Pi Setup | Install camera and test image capture       |
| 02     | ⚙️ Drive Motor Control         | Wiring and driving using L298N              |
| 03     | 🎮 Xbox Controller Integration | Connect and test manual driving             |
| 04     | 🧠 Person-Following AI         | Add OpenCV-based vision tracking            |
| 05     | 🦾 Robotic Arm (3DOF)          | Attach and control servos with PCA9685      |
| 06     | 🎯 Field Challenges            | Design tasks like pick-and-place and follow |
| 07     | 🚀 Final Integration           | Bring all systems together for demo         |

Find all `.pdf` guides in the `curriculum/` folder.

---

## 🧠 Project Features

- Raspberry Pi 5 control with OpenCV and Python
- Person-tracking AI using onboard camera
- Wireless control via Bluetooth Xbox controller
- 3-DOF robotic arm (base, shoulder, gripper)
- L298N motor driver + PWM control
- Modular open field design for activities

---

## 🔌 Electronics Bill of Materials

| Component                         | Qty |
|----------------------------------|-----|
| Raspberry Pi 5 (4GB or 8GB)      | 1   |
| Raspberry Pi Camera (v2 or v3)   | 1   |
| Xbox Wireless Controller (Bluetooth) | 1 |
| L298N Motor Driver               | 1   |
| DC Motors (12V)                  | 2   |
| PCA9685 PWM Servo Driver         | 1   |
| Servo Motors (MG90S/MG996R)      | 3   |
| 5V 3A–5A BEC / Buck Converter    | 1   |
| 12V Li-ion/Li-Po Battery Pack    | 1   |
| Jumper Wires, Capacitor (1000uF) | —   |

📎 See `docs/bom.pdf` for the printable parts list.

---

## 🛠️ Software Stack

- Python 3 (preinstalled on Raspberry Pi OS)
- OpenCV (`cv2`) for vision tracking
- `gpiozero` for motor control
- `pygame` or `evdev` for gamepad input
- `adafruit-circuitpython-pca9685` for arm servos

> All install instructions are inside each module guide.

---

## 🧭 Project Folder Structure

```bash
afrobotics/
├── README.md
├── curriculum/               # Step-by-step learning modules (.pdf)
├── docs/                     # BOM, schematics, guides
├── hardware/                 # Wiring diagrams, 3D files
├── code/
│   ├── main.py               # Main robot control loop
│   ├── control/
│   │   ├── gamepad.py
│   │   └── bluetooth_gamepad.py
│   └── hardware/
│       ├── arm.py
│       ├── motors.py
│       └── pca9685_setup.py
