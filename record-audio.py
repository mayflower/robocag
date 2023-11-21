import sounddevice as sd
from scipy.io.wavfile import write

from openai import OpenAI
client = OpenAI()


# fs = 44100  # Sample rate
# seconds = 3  # Duration of recording

# myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
# sd.wait()  # Wait until recording is finished
# write('output.wav', fs, myrecording)  # Save as WAV file
audio_file = open("output.wav", "rb")

transcript = client.audio.transcriptions.create(model='whisper-1', file=audio_file)

print(transcript)

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=transcript.text,
)

response.stream_to_file("output_transcribed.mp3")