import imutils
import base64
import numpy as np
from json import loads, dumps
from Client import ClientStreaming
from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory

class Server(WebSocketServerProtocol):

    def __init__(self):
        WebSocketServerProtocol.__init__(self)
        self.cameras_streaming = {}
        self.terminated = False

    def onConnect(self, request):
        print("[INFO] Connection from: {}".format(request.peer))

    def onOpen(self):
        print("[INFO] WebSocket is open.")

    def onMessage(self, payload, isBinary):
        raw = payload.decode('utf-8')
        msg = loads(raw)

        if msg['type'] == 'START':
            cameras = msg['cameras']
            for camera in cameras:
                serial, url_cam = camera['serial'], camera['url_cam']
                key = serial + url_cam
                if not key in self.cameras_streaming:
                    self.cameras_streaming[key] = ClientStreaming(self, serial, url_cam)
                    self.cameras_streaming[key].start()
                    print("[INFO] {} has been added.".format(key))
                else:
                    if self.cameras_streaming[key].is_terminated():
                        try:
                            del self.cameras_streaming[key]
                        except:
                            pass
                        self.cameras_streaming[key] = ClientStreaming(self, serial, url_cam)
                        self.cameras_streaming[key].start()
                        print("[INFO] {} has been restarted.".format(key))
        
        elif msg['type'] == 'STOP':
            cameras = msg['cameras']
            for camera in cameras:
                serial, url_cam = camera['serial'], camera['url_cam']
                key = serial + url_cam
                if key in self.cameras_streaming:
                    try:
                        self.cameras_streaming[key].terminate()
                        del self.cameras_streaming[key]
                        print("[INFO] {} has been terminated.".format(key))
                    except:
                        pass
        else:
            pass
            # print("[INFO] Error in message.")

    def onClose(self, wasClean, code, reason):
        self.terminated = True
        keys = list(self.cameras_streaming.keys())
        for key in keys:
            try:
                self.cameras_streaming[key].terminate()
                del self.cameras_streaming[key]
            except:
                pass

        print("[INFO] All clients has been stoped.")

    def is_terminated(self):
        return self.terminated

if __name__ == '__main__':
	import asyncio

	factory = WebSocketServerFactory(u"ws://0.0.0.0:9002")
	factory.protocol = Server

	loop = asyncio.get_event_loop()
	coro = loop.create_server(factory, '0.0.0.0', 9002)
	server = loop.run_until_complete(coro)
	print("[INFO] WebSocket server has been created.")

	try:
		loop.run_forever()
	except (KeyboardInterrupt, SystemExit):
		pass
	finally:
		server.close()
		loop.close()
