#!/bin/python
import asyncio
import subprocess
import os
from faster_whisper import WhisperModel
import edge_tts
import time
import sounddevice as sd
import numpy as np
import tempfile
import wave
from colorama import Fore, Style

async def process_query(user_input):
    """
    Processes user input and retrieves a response from Ollama using subprocess.run().
    """
    try:
        command = ['ollama', 'run', 'myjarvis', user_input]
        print(f"{Fore.RED} thinking...{Style.RESET_ALL}")
        
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error: {result.stderr.strip()}")
            return f"Error from Ollama: {result.stderr.strip()}"
        
        response = result.stdout.strip()
        return response if response else "Please say something"
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"An unexpected error occurred: {e}"

async def speak(text):
    """
    Speaks the given text using edge_tts.
    """
    tts = edge_tts.Communicate(text=text, voice="en-AU-WilliamNeural")  
    await tts.save("temp.mp3")
    subprocess.call(["mpg123", "temp.mp3"])
    os.remove("temp.mp3")

async def record_audio(duration=6, fs=44100):
    """
    Records audio from the microphone for a given duration.
    """
    os.system("play -n synth 0.1 sine 400")
    print(f"{Fore.RED} Listening...{Style.RESET_ALL}")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.int16)
    sd.wait() 
    return audio, fs

async def save_wav(audio, fs, filename):
    """
    Saves the recorded audio to a WAV file.
    """
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(audio.tobytes())

async def transcribe_audio(model, filename):
    """
    Transcribes the audio using the Faster Whisper model.
    """
    segments, info = model.transcribe(filename)
    result_text = ""
    for segment in segments:
        result_text += segment.text  # Access the text attribute
    return result_text.strip().lower()

async def play_music(query):
    """
    Plays the chosen music using YouTube search.
    """
    search_url = f"ytdl://ytsearch:{query}"
    print(f"Playing music: {search_url}")
    music_process = subprocess.Popen(['mpv', search_url])  # Ensure mpv is installed and available in PATH
    
    # Wait for the music process to finish (i.e., when the video is closed)
    music_process.wait()
    print("Music playback ended.")

async def jarvis_listener():
    """
    Main listener function for Jarvis.
    """
    model = WhisperModel("distil-small.en")
    cava_process = subprocess.Popen(['kitty', '--', 'cava'])

    await speak("Booting up, sir.")
    await speak("I am ready, sir.")

    while True:
        try:
            audio, fs = await record_audio()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                await save_wav(audio, fs, tmpfile.name)
                text = await transcribe_audio(model, tmpfile.name)
                os.remove(tmpfile.name)

            print(f"{Fore.LIGHTYELLOW_EX}>> you have said: {Fore.BLUE} {text} {Style.RESET_ALL}")

            if "music" in text:
                await speak("What song do you want to play?")
                audio, fs = await record_audio()  # Record the song name
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                    await save_wav(audio, fs, tmpfile.name)
                    song_query = await transcribe_audio(model, tmpfile.name)
                    os.remove(tmpfile.name)

                if song_query:  # Ensure there's a valid query
                    await play_music(song_query)  # Play the song

            if "stop" in text:
                print("Stopping...")
                await speak("Goodbye, sir.")
                os.system("amixer set Master unmute")
                cava_process.terminate()  # Stop Cava
                break

            if "shut down" in text:
                await speak("Shutting down the system...")
                time.sleep(2)
                os.system("shutdown now")

            if text == "reboot":
                await speak("Rebooting the system...")
                time.sleep(2)
                os.system("reboot")

            if "update" in text:
                await speak("Updating the system...")
                time.sleep(2)
                os.system("sudo pacman -Syyu --noconfirm")
                await speak("Updated the system!")

            if "install" in text:
                await speak("Installing package...")
                time.sleep(2)
                package_name = text.split("install")[-1].strip()
                os.system(f"sudo pacman -Sy {package_name} --noconfirm")
                await speak(f"Successfully installed {package_name}")

            response = await process_query(text)
            print(f"{Fore.LIGHTYELLOW_EX}>> {response} {Style.RESET_ALL}")
            await speak(response)

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(jarvis_listener())
