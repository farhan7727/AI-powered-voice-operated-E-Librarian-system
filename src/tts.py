import os
import time
import pygame
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


class SpeechCreate:
    def __init__(self):
        self.client=OpenAI(api_key=os.getenv("OPENAI_API"))
        self.output_path = Path("../data").parent / "output.mp3"
        self.input_path=Path("../data").parent / "input.wav"
    
    def __generate_audio(self,text):
        print("Generating audio...")
        with self.client.audio.speech.with_streaming_response.create(
            model="tts-1", # Standard TTS models are 'tts-1' or 'tts-1-hd'
            voice="coral",
            input=text,
                instructions="Speak in an infromative tone as if you are a librarian and seek to exaplin the details of the book you just fetched from the shelves.",
            ) as response:
            response.stream_to_file(self.output_path)
    
    def __play_audio(self):
        
        if not self.output_path.exists():
            print("Output file not found.")
            return

        try:
            print("Librarian is speaking...")
            pygame.mixer.init()
            pygame.mixer.music.load(self.output_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)    
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        
        except Exception as e:
            print(f"Error playing the audio: {e}")

    def __cleanup(self):
        if self.input_path.exists():
            try:
                os.remove(self.input_path)
            except Exception as e:
                print(f"Error deleting the file: {e}")    
        else:
            print(f"Input file has already been removed or it does not exist.")

    def speak(self,text):
        self.__generate_audio(text)
        self.__play_audio()
        self.__cleanup()



        

