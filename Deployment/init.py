#!/usr/bin/env python3
import signal
from Controller import Controller

if __name__ == '__main__':
    try:
        host, port = '0.0.0.0', 8002
        params = None
        controller = Controller(host, port, params)
        controller.start()
        signal.pause()
    except (KeyboardInterrupt, SystemExit):
        controller.terminate()
        print("[INFO] Exit from a interpreter.")
        