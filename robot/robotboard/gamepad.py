import sys
import evdev
import threading
import time

from logger import LOGGER

X_DEFAULT = 127
Y_DEFAULT = 127


class GamePadController(threading.Thread):
    def __init__(self, stop_func, motor_controller):
        threading.Thread.__init__(self)
        self.stop_func = stop_func
        self.motor_controller = motor_controller
        self.x = X_DEFAULT
        self.y = Y_DEFAULT

    def __del__(self):
        LOGGER.info("GamePadController exited")

    def run(self):
        LOGGER.info("GamePadController started")
        while not self.stop_func():
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            gamepad = None
            for device in devices:
                if "playstation" in device.name.lower():
                    gamepad = device
                    break

            if not gamepad:
                time.sleep(1)
                continue

            LOGGER.info("GamePad detected: {} {} {}".format(device.path, device.name, device.phys))

            while not self.stop_func():
                event = gamepad.read_one()
                if not event:
                    continue

                if not isinstance(event, evdev.events.InputEvent):
                    continue

                if event.type != 3:
                    continue

                if event.code == 0:
                    self.x = event.value
                elif event.code == 1:
                    self.y = event.value
                else:
                    continue
                self.motor_controller.set_input(self.x, self.y)
                print("{};{}       ".format(self.x, self.y), end="\r", flush=True)
