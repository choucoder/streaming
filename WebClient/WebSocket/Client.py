import time
import socket
import base64
from json import dumps
from threading import Thread

class ClientStreaming(Thread):

	HEADERSIZE = 10
	buffer_len = 1024

	def __init__(self, parent, serial, url_cam):
		Thread.__init__(self)
		self.parent = parent
		self.serial = serial
		self.url_cam = url_cam
		self.key = self.serial + self.url_cam
		self.terminated = False
		self.msg = {'type': 'FRAMES', 'status': '',
					'data': '', 'camera': self.key}
		# Networking attributes
		self.host, self.port = '0.0.0.0', 8002
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connected = False
		self._timeout = 10
		print("[INFO] Socket to {} has been created.".format(self.key))
		self.connect()

	def connect(self):
		if not self.connected:
			try:
				time.sleep(2)
				self.sock.connect((self.host, self.port))
				msg = 'pop ' + self.serial + ' ' + self.url_cam
				self.sock.send(bytes(msg, 'utf-8'))
				self.connected = True
				self._timeout = 10
				print("[INFO] {} has been connected.".format(self.key))
			except Exception:
				self.connected = False
				self._timeout -= 1

	def terminate(self):
		self.terminated = True
		self.connected = False
		self.sock.close()
		try:
			del self.parent.cameras_streaming[self.key]
		except:
			pass
		print("[INFO] {} has been terminated.".format(self.key))

	def prepare_recv(self, frame_len):
		msg_len = len(str(frame_len)) + self.HEADERSIZE + frame_len
		to_recv_len = msg_len

		if to_recv_len <= self.buffer_len:
			return self.buffer_len
		else:
			slices = int(to_recv_len / self.buffer_len)
			rest = to_recv_len % self.buffer_len
			if rest != 0:
				slices += 1
				return slices * self.buffer_len
			return slices * self.buffer_len

	def run(self):

		full_frame = ''
		new_frame = True

		while not self.terminated and not self.parent.terminated:

			while not self.connected and self._timeout > 0:
				self.connect()
				if self.terminated or self.parent.terminated:
					break

			if not self._timeout:
				break

			if self.terminated or self.parent.terminated:
				break

			try:
				frame = self.sock.recv(1024)
				frame = frame.decode('utf-8')

				if new_frame:
					if not frame[: self.HEADERSIZE]:
						break
					frame_len = int(frame[: self.HEADERSIZE])
					data_len = self.prepare_recv(frame_len)
					new_frame = False
				
				full_frame += frame

				if len(full_frame) == data_len:
					headers = len(str(frame_len)) + self.HEADERSIZE
					frame = full_frame[headers: frame_len + headers]
					self.msg['data'] = frame
					self.msg['status'] = "OK"	
					msg = dumps(self.msg).encode('utf8')
					try: 
						self.parent.sendMessage(msg)
					except: 
						break
					full_frame = ''
					new_frame = True
			except Exception:
				self.connected = False

		self.terminate()