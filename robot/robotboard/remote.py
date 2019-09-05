#!/usr/bin/env python3
import os
import socket
import sys
import threading
import time

from logger import LOGGER

BIND_IP = "0.0.0.0"
BIND_PORT = 51000


class RemoteController(threading.Thread):
    def __init__(self, stop_func):
        threading.Thread.__init__(self)
        self.stop_func = stop_func
        self.socket_thread = None

    def _handle_client_thread(self, client_socket):
        while not self.stop_func():
            self._handle_client(client_socket)
            time.sleep(0.10)

    def _handle_client(self, client_socket):
        request = client_socket.recv(1024)
        if not request:
            return
        request = request.strip()

        if request == b"ping":
            client_socket.send(b"pong\n")
        elif request == b"shutdown":
            LOGGER.info("Shuting down...")
            os.system("sudo poweroff")
        else:
            LOGGER.info("Received unknown message: {}".format(request))

    def stop(self):
        self.server.shutdown(socket.SHUT_RDWR)

    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((BIND_IP, BIND_PORT))
        self.server.listen(1)
        LOGGER.info("Listening on {}:{}".format(BIND_IP, BIND_PORT))

        while not self.stop_func():
            try:
                client_sock, address = self.server.accept()
            except Exception as exception:
                if not self.stop_func():
                    # Ignoring exception if stopping
                    LOGGER.warning(str(exception))
                break
            LOGGER.info("Accepted connection from {}:{}".format(address[0], address[1]))
            self.socket_thread = threading.Thread(target=self._handle_client_thread, args=(client_sock,))
            self.socket_thread.start()
