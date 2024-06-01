import os
import io
import base64
import requests

from openai import OpenAI
from fastapi import FastAPI, UploadFile, HTTPException, status as st
from tempfile import NamedTemporaryFile

import pyaudio
import wave
from pydub import AudioSegment
import simpleaudio as sa

import serial

app = FastAPI()

client = OpenAI()

# In-memory storage for message history:
messages = [{"role": "system", "content": 
    """
    You are an interactive, enthusiastic, very friendly assistant, giving concise information 
    about specific museum exhibits in 1-2 short sentences. 
    You will be given information about the exhibit you should talk about - do not contradict this information. 
    Concisely, in 1-2 short sentences, talk about the exhibit, casually chat with the user, follow their prompts.
    """}]


def speech_to_text(audio_path: str) -> str: 
    audio_file = open(audio_path, "rb")
    return client.audio.transcriptions.create(model="whisper-1", file=audio_file).text


def text_to_speech(text: str) -> str: 
    response = client.audio.speech.create(model="tts-1", voice="alloy", input=text)
    audio_content = response.content
    # Base64 encoding the audio:
    return base64.b64encode(audio_content).decode("utf-8")


def create_temporary_audio_file(audio_content: bytes) -> str:
    # OpenAI API requires the audio file path, so saving it temporarily:
    # (delete=False prevents automatic deletion after closing)
    with NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio_file:
            temp_audio_file.write(audio_content)
            return temp_audio_file.name


async def process_message(exhibit_info: str, audio: UploadFile = None, audio_path=None):

    try:
        if audio_path is None:
            # Reading and temporarily saving the audio:
            audio_content = await audio.read()
            audio_path = create_temporary_audio_file(audio_content)

        # Converting the audio to text:
        user_text = speech_to_text(audio_path)
        print("Input text converted to speech")

        # Deleting the audio file (since it's no longer needed):
        os.remove(audio_path)

        # Sending the exhibit info and user text to GPT and getting the response text:
        response_text = send_message(exhibit_info, user_text)
        print(f"Response obtained from GPT4.o: {response_text}")

        # Converting the response text to audio:
        audio_output = text_to_speech(response_text)
        print("GPT4.o response converted to audio")
            
        return {"text": response_text, "audio": audio_output}

    except Exception as e:
        print(f"Error occurred.")
        raise HTTPException(status_code=st.HTTP_400_BAD_REQUEST, detail="Unable to process input") from e

    finally:
        if audio is not None:
            await audio.close()


def send_message(exhibit_info: str, user_text: str) -> str:
    global messages

    # Adding the exhibit information to the message history:
    messages.append({"role": "system", "content": f"Exhibit Information: {exhibit_info}"})

    # Adding the user's query to the message history:
    add_message({"role": "user", "content": user_text})

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }

    # Sending a request with the current and previous messages:
    payload = {
        "model": "gpt-4",
        "messages": messages,
        "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Extracting the response content:
    response_data = response.json()
    response_text = response_data["choices"][0]["message"]["content"]

    # Adding ChatGPT's response to the message history:
    add_message({"role": "assistant", "content": response_text})

    # print(messages)

    return response_text


def add_message(new_message: dict, message_limit=10):
    global messages

    # Appending the new message to the conversation history:
    messages.append(new_message)
    
    # If the number of messages exceeds the limit, removing the oldest messages, except the first system message:
    if len(messages) > message_limit:
        # Preserving the first message and the last (message_limit - 1) messages
        messages = [messages[0]] + messages[-(message_limit - 1):]


# THE FOLLOWING FUNCTIONS ARE FOR THE PARTICLE TO USE THE SPEAKER AND MICROPHONE
# - Normally required if the board has speaker and microphone modules


def record_audio(file_path="audio/audio.wav", duration=5, sample_rate=44100, channels=1, chunk_size=1024) -> str:
    p = pyaudio.PyAudio()

    # Ensuring the directory of the specified file path exists:
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name): os.makedirs(dir_name, exist_ok=True)
    
    # Opening a new stream for recording:
    stream = p.open(format=pyaudio.paInt16, channels=channels, rate=sample_rate, input=True, frames_per_buffer=chunk_size)

    print("Recording...")

    frames = []
    for _ in range(0, int(sample_rate / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(data)
    
    print("Finished recording.")

    # Stopping and closing the stream:
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Saving the recorded file, overriding if it exists
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
    
    return file_path


def play_audio(encoded_audio):
    print("Playing audio...")

    # Decoding the base64 string:
    audio_bytes = base64.b64decode(encoded_audio)
    
    # Saving the audio to a file:
    with open("output.wav", "wb") as f:
        f.write(audio_bytes)
    
    # Loading the audio file
    audio = AudioSegment.from_file("output.wav")
    
    # Playing the audio:
    play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
    
    # Waiting for playback to finish before exiting:
    play_obj.wait_done()
