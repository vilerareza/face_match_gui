from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.texture import Texture
from kivy.core.image import Image as CoreImage

from framebox import FrameBox
from headerbar import HeaderBar


Builder.load_file('videobox.kv')


class VideoBox(BoxLayout):

    manager = ObjectProperty(None)
    frame_box = ObjectProperty(None)
    header_bar = ObjectProperty(None)
    bg_image = 'images/bg_normal.png'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
