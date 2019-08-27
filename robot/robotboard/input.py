#!/usr/bin/env python3
"""Input
"""
import sys
import argparse
from time import sleep
from getpass import getpass

import keyboard

RET_OK = 0
RET_KO = 1
DEFAULT_POWER = 50


class MotorController:
    def __init__(self):
        pass

    def process(self, inputs):
        if inputs.left and inputs.right:
            inputs.left = False
            inputs.right = False

        if inputs.forward and inputs.backward:
            inputs.forward = False
            inputs.backward = False

        motor_left = 0
        motor_right = 0
        power = inputs.power if inputs.power else DEFAULT_POWER

        if inputs.backward:
            power = -power

        if inputs.forward or inputs.backward:
            motor_left = power
            motor_right = power

        if inputs.left:
            motor_left /= 2
            motor_right = power

        if inputs.right:
            motor_left = power
            motor_right /= 2

        print("LEFT={} RIGHT={}".format(motor_left, motor_right))


class Inputs:
    def __init__(self):
        self.left = False
        self.right = False
        self.forward = False
        self.backward = False
        self.power = 0

    def set_left(self, active):
        self.left = active

    def set_right(self, active):
        self.right = active

    def set_forward(self, active):
        self.forward = active

    def set_backward(self, active):
        self.backward = active

    def set_power(self, value):
        self.power = value


class InputsController:
    def __init__(self):
        self.inputs = Inputs()

        # Forward
        keyboard.on_press_key("w", lambda _: self.inputs.set_forward(True))
        keyboard.on_release_key("w", lambda _: self.inputs.set_forward(False))
        # Backward
        keyboard.on_press_key("s", lambda _: self.inputs.set_backward(True))
        keyboard.on_release_key("s", lambda _: self.inputs.set_backward(False))
        # Left
        keyboard.on_press_key("a", lambda _: self.inputs.set_left(True))
        keyboard.on_release_key("a", lambda _: self.inputs.set_left(False))
        # Right
        keyboard.on_press_key("d", lambda _: self.inputs.set_right(True))
        keyboard.on_release_key("d", lambda _: self.inputs.set_right(False))
        # Power
        keyboard.on_release_key("0", lambda _: self.inputs.set_power(0))
        keyboard.on_release_key("1", lambda _: self.inputs.set_power(20))
        keyboard.on_release_key("2", lambda _: self.inputs.set_power(40))
        keyboard.on_release_key("3", lambda _: self.inputs.set_power(60))
        keyboard.on_release_key("4", lambda _: self.inputs.set_power(80))
        keyboard.on_release_key("5", lambda _: self.inputs.set_power(100))

    def __del__(self):
        keyboard.unhook_all()

    def get(self):
        return self.inputs


class Scheduler:
    def __init__(self):
        self.inputs_controller = InputsController()
        self.motor_controller = MotorController()

    def exec(self):
        try:
            while True:
                inputs = self.inputs_controller.get()
                self.motor_controller.process(inputs)
                sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting...")
            return RET_OK
        except Exception as exception:
            print(str(exception))
            return RET_KO
        return OK


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    scheduler = Scheduler()
    ret = scheduler.exec()
    if ret == RET_KO:
        print("FAIL")
        return ret
    print("SUCCESS")
    return ret


if __name__ == "__main__":
    sys.exit(main())
