try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    # Mock RPi.GPIO for testing on non-Raspberry Pi platforms
    import sys
    import types

    GPIO = types.ModuleType("RPi.GPIO")
    GPIO.BCM = GPIO.OUT = GPIO.HIGH = GPIO.LOW = GPIO.PWM = lambda *args, **kwargs: None
    GPIO.setmode = GPIO.setup = GPIO.output = GPIO.cleanup = lambda *args, **kwargs: None
    GPIO.PWM = lambda *args, **kwargs: types.SimpleNamespace(start=lambda *args, **kwargs: None,
                                                             ChangeDutyCycle=lambda *args, **kwargs: None)

import time

class MotorControl:
    def __init__(self, in1_pin, in2_pin, in3_pin, in4_pin, enA_pin, enB_pin):
        self.in1_pin = in1_pin
        self.in2_pin = in2_pin
        self.in3_pin = in3_pin
        self.in4_pin = in4_pin
        self.enA_pin = enA_pin
        self.enB_pin = enB_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.in1_pin, GPIO.OUT)
        GPIO.setup(self.in2_pin, GPIO.OUT)
        GPIO.setup(self.in3_pin, GPIO.OUT)
        GPIO.setup(self.in4_pin, GPIO.OUT)
        GPIO.setup(self.enA_pin, GPIO.OUT)
        GPIO.setup(self.enB_pin, GPIO.OUT)
        self.pwmA = GPIO.PWM(self.enA_pin, 100)  # Set frequency to 100Hz for motor A
        self.pwmB = GPIO.PWM(self.enB_pin, 100)  # Set frequency to 100Hz for motor B
        self.pwmA.start(0)  # Start with motor A off
        self.pwmB.start(0)  # Start with motor B off

    def start_motor_A(self):
        GPIO.output(self.in1_pin, GPIO.HIGH)
        GPIO.output(self.in2_pin, GPIO.LOW)
        self.pwmA.ChangeDutyCycle(100)  # Set duty cycle to 100% to start motor A

    def stop_motor_A(self):
        GPIO.output(self.in1_pin, GPIO.LOW)
        GPIO.output(self.in2_pin, GPIO.LOW)
        self.pwmA.ChangeDutyCycle(0)  # Set duty cycle to 0% to stop motor A

    def start_motor_B(self):
        GPIO.output(self.in3_pin, GPIO.HIGH)
        GPIO.output(self.in4_pin, GPIO.LOW)
        self.pwmB.ChangeDutyCycle(100)  # Set duty cycle to 100% to start motor B

    def stop_motor_B(self):
        GPIO.output(self.in3_pin, GPIO.LOW)
        GPIO.output(self.in4_pin, GPIO.LOW)
        self.pwmB.ChangeDutyCycle(0)  # Set duty cycle to 0% to stop motor B

    def set_speed_A(self, speed):
        if 0 <= speed <= 100:
            self.pwmA.ChangeDutyCycle(speed)  # Set duty cycle based on speed percentage for motor A
        else:
            raise ValueError("Speed must be between 0 and 100")

    def set_speed_B(self, speed):
        if 0 <= speed <= 100:
            self.pwmB.ChangeDutyCycle(speed)  # Set duty cycle based on speed percentage for motor B
        else:
            raise ValueError("Speed must be between 0 and 100")

if __name__ == "__main__":
    in1_pin = 24  # Example GPIO pin for IN1
    in2_pin = 23  # Example GPIO pin for IN2
    in3_pin = 27  # Example GPIO pin for IN3
    in4_pin = 22  # Example GPIO pin for IN4
    enA_pin = 25  # Example GPIO pin for ENA
    enB_pin = 17  # Example GPIO pin for ENB
    motor_control = MotorControl(in1_pin, in2_pin, in3_pin, in4_pin, enA_pin, enB_pin)
    motor_control.start_motor_A()
    time.sleep(2)
    motor_control.set_speed_A(50)
    time.sleep(2)
    motor_control.stop_motor_A()
    motor_control.start_motor_B()
    time.sleep(2)
    motor_control.set_speed_B(50)
    time.sleep(2)
    motor_control.stop_motor_B()
    # Add any additional testing or motor control logic here