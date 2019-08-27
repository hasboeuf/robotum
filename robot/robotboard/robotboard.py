#!/usr/bin/env python3
"""Robot brain
"""
import sys
import argparse
import os
import socket
import time

SOCKET_PATH = "/tmp/uv4l.socket"
RET_OK = 0
RET_KO = 1


class Controller:
    def __init__(self):
        self.socket = None
        self.client = None

    def exec(self):
        try:
            self._listen()
            while True:
                self._wait_for_connection()
                try:
                    self._process()
                except BrokenPipeError:
                    pass
        except KeyboardInterrupt:
            print("Exiting...")
            return RET_OK
        except Exception as exception:
            print(str(exception))
            return RET_KO
        finally:
            if self.client:
                self.client.close()
        return OK

    def _listen(self):
        try:
            os.unlink(SOCKET_PATH)
        except OSError:
            if os.path.exists(SOCKET_PATH):
                raise
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.socket.bind(SOCKET_PATH)
        self.socket.listen(1)

    def _wait_for_connection(self):
        print("Awaiting connection...")
        connection, client_address = self.socket.accept()
        print("Established connection with `{}`".format(client_address))
        self.client = connection

    def _process(self):
        while True:
            data = self.client.recv(16).decode("utf-8")
            print("Received message `{}`".format(data))
            self.client.sendall(b"OK")
            time.sleep(0.01)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    controller = Controller()
    ret = controller.exec()
    if ret == RET_KO:
        print("FAIL")
        return ret
    print("SUCCESS")
    return ret


if __name__ == "__main__":
    sys.exit(main())
