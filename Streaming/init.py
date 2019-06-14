import time
import signal
from Server import StreamingServer

if __name__ == '__main__':
    try:
        host, port = '0.0.0.0', 8002
        parent = None
        server = StreamingServer(parent, host, port)
        server.listen()
        signal.pause()
    except (KeyboardInterrupt, SystemExit):
        server.terminate()