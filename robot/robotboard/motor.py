import sys
import threading
import time
import math

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
X_DEFAULT = 0
Y_DEFAULT = 0


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

        self._stop()

    def __del__(self):
        GPIO.cleanup()
        LOGGER.info("MotorController exited")

    def _stop(self):
        self._move(0, 0)

    def _move(self, lpower, rpower):
        if lpower == 0:
            GPIO.output(MOTOR_LEFT_FWD_GPIO, GPIO.LOW)
            GPIO.output(MOTOR_LEFT_BWD_GPIO, GPIO.LOW)
        elif lpower > 0:
            GPIO.output(MOTOR_LEFT_FWD_GPIO, GPIO.HIGH)
            GPIO.output(MOTOR_LEFT_BWD_GPIO, GPIO.LOW)
        else:
            GPIO.output(MOTOR_LEFT_FWD_GPIO, GPIO.LOW)
            GPIO.output(MOTOR_LEFT_BWD_GPIO, GPIO.HIGH)

        if rpower == 0:
            GPIO.output(MOTOR_RIGHT_FWD_GPIO, GPIO.LOW)
            GPIO.output(MOTOR_RIGHT_BWD_GPIO, GPIO.LOW)
        elif rpower > 0:
            GPIO.output(MOTOR_RIGHT_FWD_GPIO, GPIO.HIGH)
            GPIO.output(MOTOR_RIGHT_BWD_GPIO, GPIO.LOW)
        else:
            GPIO.output(MOTOR_RIGHT_FWD_GPIO, GPIO.LOW)
            GPIO.output(MOTOR_RIGHT_BWD_GPIO, GPIO.HIGH)

        self.left_power.start(abs(lpower*2))
        self.right_power.start(abs(rpower*2))
        LOGGER.info("{} | {}".format(lpower, rpower))

    def set_input(self, x, y):
        self.x = x
        self.y = y

    def process(self):
        x = self.x
        y = self.y

        power = min(round(math.sqrt(math.pow(abs(x), 2) + math.pow(abs(y), 2))), 50)
        #LOGGER.info("{};{};{}".format(x, y, power))

        if x == 0 and y == 0:
            self._stop()
            return

        # Move straight
        if x >= -3 and x <= 3:
            if y >= 0:
                # Forward
                self._move(power, power)
            else:
                # Backward
                self._move(-power, -power)
            return
        elif x <= -47:
            # Turn left:
            # - motor left backward
            # - motor right forward
            self._move(-power, power)
            return
        elif x >= 47:
            # Turn right
            # - motor left forward
            # - motor right backward
            self._move(power, -power)
            return

        x_ratio = (x + 50) / 100
        left_power = power - power * (1 - x_ratio)
        right_power = power - power * x_ratio

        if y < 0:
            tmp = left_power
            left_power = -right_power
            right_power = -tmp

        self._move(left_power, right_power)

    def run(self):
        LOGGER.info("MotorController started")
        while not self.stop_func():
            self.process()
            time.sleep(0.1)
