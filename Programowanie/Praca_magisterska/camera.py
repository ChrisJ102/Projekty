import cv2
import threading
import time


class Camera:
    def __init__(self, settings):
        self.camera_width = settings.get("camera_width", 1920)
        self.camera_height = settings.get("camera_height", 1080)
        self.frame_id = 0  # licznik klatek
        mode = settings.get("camera_mode", 2)

        if mode == 0:
            print("[Camera] Using Raspberry Pi camera")
            pipeline = (
                "libcamerasrc ! "
                "videoconvert ! video/x-raw,format=BGR ! "
                "appsink"
            )
            self.vid = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

        elif mode == 1:
            print("[Camera] Using USB camera RP")
            self.vid = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
        else:
            print("[Camera] Using USB camera")
            self.vid = cv2.VideoCapture(0)
 
        self.frame = None
        self.lock = threading.Lock()
        self.fps = 0.0

        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        self.vid.set(cv2.CAP_PROP_FPS,60)
        actual_fps = self.vid.get(cv2.CAP_PROP_FPS)
        print(f"[Camera] {self.camera_width}x{self.camera_height} Requested FPS: 60 | Actual FPS set by device: {actual_fps}")


    def capture_frames(self):
        last_time = time.time()
        counter = 0


        while True:
            ret, frame = self.vid.read()
            if not ret:
                break

            with self.lock:
                self.frame = frame
                self.frame_id += 1  # dodajemy licznik klatek

            counter += 1
            current_time = time.time()
            if current_time - last_time >= 1.0:
                self.fps = counter / (current_time - last_time)
                #print(f"[CAMERA] FPS: {self.fps:.3f}")
                counter = 0
                last_time = current_time

    def get_frame(self):
        with self.lock:
            return self.frame, self.frame_id

    def release(self):
        """Release the camera resource."""
        self.vid.release()
