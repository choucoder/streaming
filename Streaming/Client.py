import socket
import time
import base64
from threading import Thread

class ClientStreaming(Thread):

	HEADERSIZE = 10
	buffer_len = 1024

	def __init__(self, parent, client, address, serial, camera):
		Thread.__init__(self)
		self.parent = parent
		self.client = client
		self.serial = serial
		self.camera = camera
		self.sockets = {}
		self.address = address
		self.key = self.serial + self.camera
		self.terminated = False

	def terminate(self):
		self.terminated = True
		self.client.close()

		# Deleting key from clients_push dict
		try:
			del self.parent.clients_push[self.key]
		except:
			pass
		# Deleting clients from sockets dict
		keys = list(self.sockets.keys())
		for key in keys:
			try:
				self.sockets[key].close()
				del self.sockets[key]
			except:
				pass
		print("[INFO] Client to {} has been terminated.".format(self.key))

	def is_terminated(self):
		return self.terminated

	def append(self, _socket):
		num_conn = len(self.sockets)
		self.sockets[num_conn] = _socket

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

	def sendToClients(self, frame):
		keys = list(self.sockets.keys())
		for key in keys:
			try:
				self.sockets[key].send(bytes(frame, 'utf-8'))
			except Exception:
				self.sockets[key].close()
				del self.sockets[key]

	def run(self):

		full_frame = ''
		new_frame = True

		while not self.terminated and not self.parent.is_terminated():
			try:
				frame = self.client.recv(1024)
				frame = frame.decode('utf-8')
				if new_frame:
					if not frame[: self.HEADERSIZE]:
						print("[INFO] Socket is not sending data.")
						break
					frame_len = int(frame[: self.HEADERSIZE])
					data_len = self.prepare_recv(frame_len)
					new_frame = False

				full_frame += frame

				if len(full_frame) == data_len:
					# print("[INFO] full_frame len: {}".format(len(full_frame)))
					self.sendToClients(full_frame)
					full_frame = ''
					new_frame = True

			except Exception:
				print("[INFO] Exception in while run")
				break

		self.terminate()