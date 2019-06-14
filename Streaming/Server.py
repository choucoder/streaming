import time
import socket
from threading import Thread
from Client import ClientStreaming

class StreamingServer(Thread):

    HEADERSIZE = 10
    buffer_len = 1024

    def __init__(self, parent, host, port):
        Thread.__init__(self)
        self.parent = parent
        self.host = host
        self.port = port
        self.terminated = False
        self.clients_push = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[INFO] Socket has been created.")
        self.sock.bind((self.host, self.port))
        print("[INFO] Socket has been binded.")

    def is_terminated(self):
        return self.terminated

    def listen(self, max_conn = 10):
        self.sock.listen(max_conn)
        print("[INFO] Server is listening.")

        while not self.terminated:
            client, address = self.sock.accept()
            print("[INFO] Connection from: {}".format(address))
            header = client.recv(1024)
            _type, serial, camera = header.decode('utf-8').split()
            key = serial + camera

            if _type == 'push':
                if not key in self.clients_push:
                    self.clients_push[key] = ClientStreaming(self, client, address, serial, camera)
                    self.clients_push[key].start()
            else:
                if key in self.clients_push:
                    self.clients_push[key].append(client)

    def terminate(self):
        self.terminated = True
        self.sock.close()
        keys = list(self.clients_push.keys())

        for key in keys:
            try:
                self.clients_push[key].terminate()
                del self.clients_push[key]
            except:
                pass
        print("[INFO] Streaming server has been closed.")
        



