import os
import numpy as np
import sounddevice as sd
from deepgram import Deepgram
from dotenv import load_dotenv
from scipy.io.wavfile import write
from pathlib import Path
load_dotenv()

class Transcriber:
    def __init__(self, channels=2, duration=5, fs=44100):
        self.dg=Deepgram(os.getenv("DEEPGRAM_API"))
        self.FS = fs
        self.DURATION = duration
        self.CHANNELS = channels
        self.audio_path=Path("../data").parent / "input.wav"
    
    def __record_audio(self):
        print(f"Recording for {self.DURATION} seconds... You may speak now.")
        recording = sd.rec(int(self.DURATION * self.FS), 
                    samplerate=self.FS,
                    channels=self.CHANNELS, 
                    dtype='float64')
        sd.wait()

        print(f"Recording stopped. Saving to {self.audio_path}...")
        write(self.audio_path, self.FS, recording)

    def __transcribe_audio(self):
        try:
            with open(self.audio_path, 'rb') as audio:
                source = {'buffer': audio, 'mimetype': 'audio/wav'}
                options = {
                    'punctuate': True,
                    'language': 'en',
                    'model': 'nova-3' 
                }

                response = self.dg.transcription.sync_prerecorded(source, options)
                transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
                return transcript
    
        except Exception as e:
            print(f"STT error: {e}")
            return None
        
    def input_audio(self):
        self.__record_audio()
        return self.__transcribe_audio()