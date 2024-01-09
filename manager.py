import os
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from videobox import VideoBox

Builder.load_file('manager.kv')

class Manager(BoxLayout):

    video_box = ObjectProperty()

    def stop(self):
        pass