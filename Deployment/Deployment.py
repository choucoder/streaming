import socket
import time
from threading import Thread
from cv2 import VideoCapture
from Client import ClientStreaming

class Deployment(Thread):
    
    def __init__(self, parent, params, host, port):
        Thread.__init__(self)
        self.parent = parent
        self.params = params
        self.terminated = False
        self.client_streaming = {}
        self.serial = 'aeiou12345'
        self.email = 'email'
        # Network StreamingServer params 
        self.host, self.port = host, port

    def isOnline(self, camera):
        try:
            cam = VideoCapture(camera)
            ret, frame = cam.read()
            cam.release()
            if not ret and not frame:
                print("[INFO] Camera {} is offline.".format(camera))
                return False
            print("[INFO] Camera {} is online.".format(camera))
            return True
        except Exception:
            print("[INFO] Has occurred an error in isOnCamera to {}".format(camera))
            return False

    def run(self):
        while not self.terminated and not self.parent._terminated:
            time.sleep(10)
            # Get cameras from api sending email and serial
            cameras_url = ['video.mp4']
            """ Verify if the urls obtained from api are  
                available for send frames to the Server
            """
            if self.terminated:
                break

            for camera in cameras_url:
                if self.isOnline(camera) and not camera in self.client_streaming:
                    # Create a ClientStreaming to sending 
                    # frames from the camera obtained
                    self.client_streaming[camera] = ClientStreaming(self, camera, 
                    self.host, self.port)
                    self.client_streaming[camera].start()
        # Terminate the Deployment Instance Thread
        if not self.terminated:
            self.terminate()
        else:
            print("[INFO] Another Thread has terminated the processes")

    def terminate(self):
        self.terminated = True

        print("[INFO] Deleting ClientStreamings")
        keys = list(self.client_streaming.keys())

        for cs in keys:
            try:
                self.client_streaming[cs].terminate()
                del self.client_streaming[cs]
                print("[INFO] {} was deleted".format(cs))
            except Exception:
                print("[INFO] {} was deleted by itself".format(cs))

    def is_terminated(self):
        return self.terminated

