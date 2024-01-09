from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout

Builder.load_file('headerbar.kv')


class HeaderBar(FloatLayout):

    manager = ObjectProperty(None)
    frame_box = ObjectProperty(None)
    btn_play = ObjectProperty(None)
    score_text = StringProperty('Match Score: 0.0%')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Callback function for buttons press event
    def button_press_callback(self, btn):
        if btn == self.btn_play:
            # Play button is pressed
            pass
    
    # Callback function for buttons release event
    def button_release_callback(self, btn):
        if btn == self.btn_play:
            # Play button is released
            self.parent.frame_box.play()