import RPi.GPIO as GPIO

class MotorControl:
    def __init__(self, motor_pin):
        self.motor_pin = motor_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.motor_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.motor_pin, 100)  # Set frequency to 100Hz
        self.pwm.start(0)  # Start with motor off

    def start_motor(self):
        self.pwm.ChangeDutyCycle(100)  # Set duty cycle to 100% to start the motor

    def stop_motor(self):
        self.pwm.ChangeDutyCycle(0)  # Set duty cycle to 0% to stop the motor

    def set_speed(self, speed):
        if 0 <= speed <= 100:
            self.pwm.ChangeDutyCycle(speed)  # Set duty cycle based on speed percentage
        else:
            raise ValueError("Speed must be between 0 and 100")

if __name__ == "__main__":
    motor_pin = 18  # Example GPIO pin
    motor_control = MotorControl(motor_pin)
    motor_control.start_motor()
    # Add any additional testing or motor control logic here