import speech_recognition as sr
from openai import OpenAI
from os import path
import pygame

# Initialize the recognizer
recognizer = sr.Recognizer()

# Set the microphone as the audio source
microphone = sr.Microphone()

pygame.mixer.init()

voice_client = OpenAI()

speech_file_path = path.join(path.curdir, "speech.mp3")


# Adjust for ambient noise
with microphone as source:
    print("Adjusting for ambient noise. Please wait...")
    recognizer.adjust_for_ambient_noise(source)
    print("Ambient noise adjustment complete.")



  
def human_voice_input(question) -> str:
    response = voice_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=question
    )
    response.stream_to_file(speech_file_path)
    pygame.mixer_music.load(speech_file_path)
    pygame.mixer_music.play()
    while pygame.mixer.music.get_busy():
      pygame.time.Clock().tick(10)

    with microphone as source:
      audio_data = recognizer.listen(source, timeout=10)
      text = recognizer.recognize_whisper_api(audio_data)
      return text
