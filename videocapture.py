import queue
import threading

import cv2 as cv


# bufferless VideoCapture
class VideoCapture:

    def __init__(self, name):
        self.name = name
        self.cap = cv.VideoCapture(name)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()


    def init_video_cap(self, name):
        video_cap = cv.VideoCapture(name)
        return video_cap


    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                # Reinit video cap
                self.cap = self.init_video_cap(self.name)
                continue
            if not self.q.empty():
                try:
                    self.q.get_nowait()   # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        return self.q.get()