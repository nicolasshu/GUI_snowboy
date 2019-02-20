from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import snowboydecoder
import signal
import numpy as np
import speech_recognition as sr
import os
import sys

import threading

interrupted = False
model='./jarvis.pmdl'

def signal_handler(signal, frame):
    global interrupted
    interrupted = True
def interrupt_callback():
    global interrupted
    return interrupted


class MainLayout(BoxLayout):
    def listen(self):
        threading.Thread(target=self.update_text).start()
    def update_text(self):
        button_options = ['Start to Listen','Listening...']
        try:
            self.opt += 1
        except:
            self.opt = 1

        self.opt = self.opt % 2
        self.button_text.text = button_options[self.opt]
        print('key: ',self.opt)
        if self.opt == 1:
            # signal.signal(signal.SIGINT, signal_handler)
            self.detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
            self.detector.start(detected_callback=snowboydecoder.play_audio_file,
                           interrupt_check=interrupt_callback,
                           audio_recorder_callback=self.audioRecorderCallback,
                           sleep_time=0.03)
            self.detector.terminate()
        else:
            self.detector.terminate()


    def audioRecorderCallback(self,fname):
        print('\n\n\n\n\n\n')
        print("converting audio to text")

        # time.sleep(1)
        r = sr.Recognizer()
        with sr.AudioFile(fname) as source:
            r.adjust_for_ambient_noise(source)
            audio = r.record(source)
        try:
            mytext = r.recognize_google(audio)
            print(mytext)
            self.text_label.text = mytext

            data = audio.get_wav_data()
            data = np.fromstring(data,'Int16')

            if mytext=='shut down':
                self.update_text()
                print('here')
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

        os.remove(fname)

class StructureApp(App):
    def build(self):
        app = MainLayout()
        return app

if __name__ == '__main__':
    StructureApp().run()
