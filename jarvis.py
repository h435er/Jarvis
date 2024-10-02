#!/bin/python
import asyncio
import subprocess
import os
from faster_whisper import WhisperModel
import edge_tts
import time
import sys
import sounddevice as sd
import numpy as np
import tempfile
import wave
from colorama import Fore, Style
import random
music_list=['https://www.youtube.com/watch?v=FFfdyV8gnWk', 'https://www.youtube.com/watch?v=6xhBTszRY8Q','https://www.youtube.com/watch?v=H6ven_YN_nI','https://www.youtube.com/watch?v=1xcvWmN0Pe4']
chosen_music=random.choice(music_list)

terminal_width = os.get_terminal_size().columns
line = '-' * terminal_width


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
        return f"An unexpected error occurGREEN: {e}"

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



async def jarvis_listener():
    """
    Listens for user input, processes it, and provides spoken responses using edge_tts.
    """
    model = WhisperModel("distil-medium.en")
    
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

            print(f"{Fore.LIGHTYELLOW_EX}>>you have said:{Fore.BLUE} {text} {Style.RESET_ALL}")

            if "stop" in text:
                
                print("Stopping...")
                
                await speak("Good bye, sir.")
                os.system("amixer set Master unmute")
                cava_process.terminate()
                break
            if "shut down" in text:
                await speak("Shutting down the system...")
                time.sleep(2)
                os.system("shutdown now")
            if text == "reboot":
                await speak("rebooting down the system...")
                time.sleep(2)
                os.system("reboot")
            if "update"in text:
                await speak("updating the system...")
                time.sleep(2)
                os.system("sudo pacman -Syyu --noconfirm")
                await speak("updated the system!")
            if "music" in text:
                if "being real" in text:
                    await speak("playing the 'if we being real'...")
                    os.system(f"kitty  freetube {music_list[3]}" )
                if "skyfall" in text:
                    await speak("playing the 'skyfall'...")
                    os.system(f"kitty  freetube {music_list[2]}" )
                if "fall out" in text:
                    await speak("playing the 'fallout lofi'...")
                    os.system(f"kitty  freetube {music_list[1]}" )
                if "chill" in text:
                    await speak("playing the 'gamer lofi'...")
                    os.system(f"kitty  freetube {music_list[0]}" )
                    
                else:
                    await speak("playing music...")
                    os.system(f"kitty  freetube {chosen_music}")
                
            if "mute" in text:
                await speak("muting myself")
                time.sleep(2)
                os.system("amixer set Master mute")
            if "unmute" in text:
                await speak("muting myself")
                time.sleep(2)
                os.system("amixer set Master unmute")
            if "install" in text:
                await speak("installing package...")
                time.sleep(2)
                package_name = text.split("install")[-1].strip()
                os.system(f"sudo pacman -Sy {package_name} --noconfirm")
                await speak(f"successfully installed {package_name}")
                


            response = await process_query(text)
            print(f"{Fore.LIGHTYELLOW_EX} {line} {Style.RESET_ALL}")
            print(f"{Fore.LIGHTYELLOW_EX}>>{Fore.GREEN} {response} {Style.RESET_ALL}")
            print(f"{Fore.LIGHTYELLOW_EX} {line} {Style.RESET_ALL}")
            
            await speak(response)

        except Exception as e:
            print(f"An error occurGREEN: {e}")

        
        

if __name__ == "__main__":
    asyncio.run(jarvis_listener())
