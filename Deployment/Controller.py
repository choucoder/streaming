import time
from threading import Thread
from Deployment import Deployment

class Controller(Thread):

    def __init__(self, host, port, params):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.params = params
        self._terminated = False
        self.deployment = Deployment(self, params, host, port)

    def run(self):

        self.deployment.start()

        while not self._terminated:
            print("[INFO] ControllerThread is running.")
            time.sleep(2)
        print("[INFO] Exiting from ControllerThread.")

    def terminate(self):
        self._terminated = True
        self.deployment.terminate()