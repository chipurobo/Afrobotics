#!/usr/bin/env python3
from gpiozero import Motor, PWMOutputDevice
from time import sleep
from src.lidar.lidar_control import LidarControl  # Use absolute import

# Define motors (direction control)
motor_a = Motor(forward=17, backward=27)  # Motor A: IN1 and IN2
motor_b = Motor(forward=22, backward=23)  # Motor B: IN3 and IN4

# Define enable pins using GPIO 24 and GPIO 25
enable_a = PWMOutputDevice(24)  # ENA for Motor A
enable_b = PWMOutputDevice(25)  # ENB for Motor B

# Set enable pins to half speed
enable_a.value = 0.5  # 50% duty cycle for Motor A
enable_b.value = 0.5  # 50% duty cycle for Motor B

def move_forward():
    motor_a.forward()
    motor_b.forward()

def stop_motors():
    motor_a.stop()
    motor_b.stop()

def avoid_obstacle():
    lidar_control = LidarControl(port='/dev/ttyUSB0')
    try:
        for scan in lidar_control.lidar.iter_scans():
            distances = [distance for (_, _, distance) in scan]
            if any(distance < 500 for distance in distances):  # Obstacle within 500 mm
                print("Obstacle detected! Stopping motors.")
                stop_motors()
                break
            else:
                move_forward()
                sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping scan...")
    finally:
        lidar_control.stop_scan()

if __name__ == "__main__":
    avoid_obstacle()