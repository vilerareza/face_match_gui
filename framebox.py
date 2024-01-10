import time
import math
from functools import partial
from threading import Condition, Thread

import cv2 as cv
import dlib
import numpy as np

from kivymd.app import App
from kivy.clock import Clock
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image

import face_recognition



Builder.load_file('framebox.kv')


class FrameBox(Image):

    manager = ObjectProperty(None)

    video_cap = None
    condition = Condition()
    state = 'stop'

    bg_normal = 'images/bg_normal.png'
    bg_green = 'images/bg_green.png'
    bg_yellow = 'images/bg_yellow.png'
    bg_red = 'images/bg_red.png'
    title_match_ok = 'images/match_ok.png'
    title = 'images/title.png'


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.texture = Texture.create()
        # dlib face detector
        self.face_detector = dlib.get_frontal_face_detector()


    def on_parent(self, *args):
        if self.parent:
            print ('Ready')
            # Start the camera stream
            self.play()
            print(App.get_running_app().manager)


    def play(self):

        if self.state == 'stop':
            # Stop to play
            with self.condition:
                self.state = 'play'
                self.condition.notify_all()
            self.play_thread = Thread(target = self.play_)
            self.play_thread.daemon = True
            self.play_thread.start()

        elif self.state == 'play':
            # Play to pause
            with self.condition:
                self.state = 'pause'
                self.condition.notify_all()

        elif self.state == 'pause':
            # Pause to play
            with self.condition:
                self.state = 'play'
                self.condition.notify_all()


    def play_(self):

        try:

            # self.rtsp = self.manager.rtsp

            # Initialize capture object
            # self.video_cap = cv.VideoCapture(0)
            self.video_cap = cv.VideoCapture('rtsp://admin:Smartcity07@192.168.1.39:554/Streaming/channels/101')

            ### Get video properties            
            # frame_w = int(self.video_cap.get(cv.CAP_PROP_FRAME_WIDTH))
            # frame_h = int(self.video_cap.get(cv.CAP_PROP_FRAME_HEIGHT))
            frame_w = 640
            frame_h = 480
            # print (frame_w, frame_h)
            # Calculate adjusted  size (640px target width)
            # new_frame_w = 640
            # size_factor = new_frame_w/frame_w
            # new_frame_h = int(frame_h*size_factor)
            
            # Creating texture
            # self.texture = Texture.create(size=(new_frame_w, new_frame_h), colorfmt="rgb")
            self.texture = Texture.create(size=(frame_w, frame_h), colorfmt="rgb")

        except Exception as e:
            print (e, 'Camera not found')
            # Reset the playing flag
            self.state = 'stop'
            self.video_cap.release()
            return


        ### Video Loop
        while (self.video_cap.isOpened()):

            if self.state=='pause':
                with self.condition:
                    self.condition.wait()

            elif self.state == 'stop':
                # Stop
                # Release video capture object
                self.video_cap.release()
                # Create blank texture
                self.texture = Texture.create()
                break

            # Reading frame
            t1=time.time()
            ret, frame = self.video_cap.read()

            if ret:
                # Resize the frame to the adjusted size
                frame = cv.resize(frame, (frame_w, frame_h))
                print(frame_w, frame_h)
                faces, frame = self.detect_face(frame)

                if len(faces)==2:

                    vectors = []
                    for face in faces:
                        face = face[:,:,::-1]
                        vector = face_recognition.api.face_encodings(face)
                        vectors.append(vector)

                    if len(vectors[0]) > 0 and len (vectors[1]) > 0:
                        distance = face_recognition.api.face_distance([vectors[0][0]], vectors[1][0])
                        # result = face_recognition.api.compare_faces([vectors[0][0]], vectors[1][0])
                        # print (distance, result)
                        # score = self.face_confidence(distance[0])
                        score = 1.3 - distance[0]
                        score = min(1.0, score)

                        # print ('Score: ', score)

                        if score <0.6:
                            Clock.schedule_once(partial(self.change_bg_img, self.bg_red), 0)
                            self.header_bar.score_text = f'Match Score: {str(round(score*100, 1))}%'
                        elif score >=0.6 and score <0.8:
                            Clock.schedule_once(partial(self.change_bg_img, self.bg_yellow), 0)
                            self.header_bar.score_text = f'Match Score: {str(round(score*100, 1))}%'

                        # MATCH OK
                        elif score >= 0.8:
                            Clock.schedule_once(partial(self.change_bg_img, self.bg_green), 0)
                            Clock.schedule_once(partial(self.change_title_img, self.title_match_ok), 0)
                            self.header_bar.score_text = f'Match Score: {str(round(score*100, 1))}%'
                
                else:
                    Clock.schedule_once(partial(self.change_bg_img, self.bg_normal), 0)
                    Clock.schedule_once(partial(self.change_title_img, self.title), 0)
                    self.header_bar.score_text = 'Match Score: 0.0%'


                frame = cv.flip(frame,0)
                frame = frame[:,:,::-1]
                # print (frame.dtype, frame.shape)
                self.on_frame_(frame)
                cv.waitKey(1)
                t2 = time.time()

            else:
                print ('End of the stream')
                # Create blank texture
                self.texture = Texture.create()
                # Reset play button image and disable it      
                # Clock.schedule_once(partial(self.change_play_btn_img, 'images/play.png'), 0)
                # Reset the playing flag
                self.state = 'stop'
                # Release video capture object
                self.video_cap.release()
                break


    # Update the livestream texture with new frame
    def update_frame(self, buff_, *largs):
        data = buff_.flatten()
        self.texture.blit_buffer(data, bufferfmt="ubyte", colorfmt="rgb")
        self.canvas.ask_update()
    
    
    # Update the livestream texture with new frame
    def on_frame_(self, img_array):
        Clock.schedule_once(partial(self.update_frame, img_array), 0)


    def get_face_rect(self, img, dlib_rect):
        x1 = int(max(0, dlib_rect.left()))
        y1 = int(max(0, dlib_rect.top()))
        x2 = int(min(dlib_rect.right(), img.shape[1]))
        y2 = int(min(dlib_rect.bottom(), img.shape[0]))
        return [(x1,y1), (x2,y2)]


    def detect_face(self, img, bbox = True):
        
        # Conversion to gray
        img_gray = cv.cvtColor(img.copy(), cv.COLOR_BGR2GRAY)
        # Face detection
        boxes = self.face_detector(img_gray, 0)
        # print (len(boxes), boxes)
        # Process on face exists
        faces = []
        if len(boxes) > 0:
        
            for box in boxes:    
                # Draw rectangle on faces
                if bbox:
                    start_pt, end_pt = self.get_face_rect(img, box)
                    cv.rectangle(img, 
                                start_pt,
                                end_pt, 
                                (0,255,0), 
                                3)
                    
                # if len(boxes) == 2:
                face = img[start_pt[1]:end_pt[1], 
                            start_pt[0]:end_pt[0], 
                            :]
                faces.append(face)
        
        return faces, img


    def face_confidence(self, distance, thresh=0.6):
        range = (1.0 - thresh)
        linear_val = (1.0-distance) / (range*2.0)

        if distance > thresh:
            return round(linear_val *100, 2)
        else:
            value = (linear_val * ((1.0-linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
            return (round(value, 2))

    def find_distance_cos(self, vector_1, vector_2):
        # Cosine distance
        dot = np.dot(vector_1, vector_2)
        norm = np.linalg.norm (vector_1) * np.linalg.norm (vector_2)
        similarity = dot / norm
        return similarity
    
    def change_bg_img(self, img_path, *args):
        with self.canvas.before:
            Rectangle(pos=self.pos, size=self.size, source = img_path)

    def change_title_img(self, img_path, *args):
        self.header_bar.title_img.source = img_path