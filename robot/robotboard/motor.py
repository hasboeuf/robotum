import sys
import threading
import time

try:
    from RPi import GPIO
except:
    print("GPIO not found, mocking it!")
    from unittest.mock import MagicMock

    GPIO = MagicMock()

from logger import LOGGER

MOTOR_LEFT_POWER_GPIO = 18
MOTOR_LEFT_FWD_GPIO = 17
MOTOR_LEFT_BWD_GPIO = 27
MOTOR_RIGHT_POWER_GPIO = 13
MOTOR_RIGHT_FWD_GPIO = 6
MOTOR_RIGHT_BWD_GPIO = 5
X_DEFAULT = 127
Y_DEFAULT = 127


class MotorController(threading.Thread):
    def __init__(self, stop_func):
        threading.Thread.__init__(self)
        self.stop_func = stop_func
        self.x = X_DEFAULT
        self.y = Y_DEFAULT

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTOR_LEFT_POWER_GPIO, GPIO.OUT)
        GPIO.setup(MOTOR_LEFT_FWD_GPIO, GPIO.OUT)
        GPIO.setup(MOTOR_LEFT_BWD_GPIO, GPIO.OUT)
        GPIO.setup(MOTOR_RIGHT_POWER_GPIO, GPIO.OUT)
        GPIO.setup(MOTOR_RIGHT_FWD_GPIO, GPIO.OUT)
        GPIO.setup(MOTOR_RIGHT_BWD_GPIO, GPIO.OUT)

        self.left_power = GPIO.PWM(MOTOR_LEFT_POWER_GPIO, 100)
        self.right_power = GPIO.PWM(MOTOR_RIGHT_POWER_GPIO, 100)

        self.set_left(0)
        self.set_right(0)

    def __del__(self):
        GPIO.cleanup()
        LOGGER.info("MotorController exited")

    def set_left(self, power):
        self.left_power.start(power)
        if power == 0:
            GPIO.output(MOTOR_LEFT_FWD_GPIO, GPIO.LOW)
            GPIO.output(MOTOR_LEFT_BWD_GPIO, GPIO.LOW)
        elif power > 0:
            GPIO.output(MOTOR_LEFT_FWD_GPIO, GPIO.HIGH)
            GPIO.output(MOTOR_LEFT_BWD_GPIO, GPIO.LOW)
        else:
            GPIO.output(MOTOR_LEFT_FWD_GPIO, GPIO.LOW)
            GPIO.output(MOTOR_LEFT_BWD_GPIO, GPIO.HIGH)

    def set_right(self, power):
        self.right_power.start(power)
        if power == 0:
            GPIO.output(MOTOR_RIGHT_FWD_GPIO, GPIO.LOW)
            GPIO.output(MOTOR_RIGHT_BWD_GPIO, GPIO.LOW)
        elif power > 0:
            GPIO.output(MOTOR_RIGHT_FWD_GPIO, GPIO.HIGH)
            GPIO.output(MOTOR_RIGHT_BWD_GPIO, GPIO.LOW)
        else:
            GPIO.output(MOTOR_RIGHT_FWD_GPIO, GPIO.LOW)
            GPIO.output(MOTOR_RIGHT_BWD_GPIO, GPIO.HIGH)

    def set_input(self, x, y):
        self.x = x
        self.y = y

    def process(self):
        LOGGER.info("{};{}".format(self.x, self.y))

    def run(self):
        LOGGER.info("MotorController started")
        while not self.stop_func():
            self.process()
            time.sleep(0.1)
