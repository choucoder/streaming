import socket
import time
import base64
import imutils
from cv2 import VideoCapture, imencode
from threading import Thread

class ClientStreaming(Thread):

	HEADERSIZE = 10
	buffer_len = 1024

	def __init__(self, parent, camera, host, port):
		Thread.__init__(self)
		self.parent = parent
		self.camera = camera
		self.terminated = False
		# Network parameters
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connected = False
		self._reconnect = 10
		# Camera parameters
		self._camera = None
		self._online = False
		self._timeout = 10

	def connect(self):
		try:
			time.sleep(1)
			if not self.connected:
				self.sock.connect((self.host, self.port))
				msg = 'push ' + self.parent.serial + ' ' + self.camera
				self.sock.send(bytes(msg, 'utf-8'))
				self.connected = True
				self._reconnect = 10
				print("[INFO] {} is connected.".format(self.camera))
		except Exception:
			self.connected = False
			print("[INFO] Failed trying connect with {}".format(self.camera))

	def openStream(self):
		try:
			time.sleep(1)
			if not self._online:
				self._camera = VideoCapture(self.camera)
				self._online = True
				self._timeout = 10
				print("[INFO] VideoCapture({}) is open.".format(self.camera))
		except Exception:
			self._online = False
			print("[INFO] Failed VideoCapture({}).".format(self.camera))

	def prepare_data_send(self, to_send, to_send_len):
		if to_send_len <= self.buffer_len:
			fill = self.buffer_len - to_send_len
			return to_send + "0"*fill
		else:
			slices = int(to_send_len / self.buffer_len)
			rest = to_send_len % self.buffer_len
			if rest != 0:
				slices += 1
				new_len = slices * self.buffer_len
				fill = new_len - to_send_len
				return to_send + "0"*fill
			return to_send

	def run(self):
		
		self.connect()
		self.openStream()

		while not self.terminated and not self.parent.is_terminated():
			
			while not self._online and self._timeout > 0:
				self.openStream()
				self._timeout -= 1

			while not self.connected and self._reconnect > 0 and self._timeout > 0:
				self.connect()
				self._reconnect -= 1

			if not self._timeout or not self._reconnect:
				break
			try:
				ret, frame = self._camera.read()
				if not ret:
					break
				frame = imutils.resize(frame, width=200, height=200)
				_, image = imencode('.jpg', frame)
				bframe = base64.b64encode(image)
				frame = bframe.decode('utf-8')

				frame_len = len(frame)
				data = str(frame_len) + (" "*self.HEADERSIZE) + frame
				data_len = len(data)
				
				data = self.prepare_data_send(data, data_len)
				# print("[INFO] len data: {}".format(len(data)))
				bytes_data = bytes(data, 'utf-8')
				self.sock.send(bytes_data)

			except Exception:
				self.terminate()
		
		try:
			self.terminate()
			print("[INFO] ClientStreaming({}) has been terminated.".format(self.camera))
		except Exception:
			print("[INFO] ClientStreaming({}) was terminated already.".format(self.camera))

	def terminate(self):
		self.terminated = True
		self.connected = False
		self._online = False
		self.sock.close()
		self._camera.release()

		try:
			del self.parent.client_streaming[self.camera]
			print("[INFO] Deleting {} from ClientStreaming.".format(self.camera))
		except Exception:
			print("[INFO] Error trying to delete {} from ClientStreaming".format(self.camera))