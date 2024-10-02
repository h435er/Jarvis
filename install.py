#!/bin/python
#Install script for the jarvis ai
import os
import time
print("""


   ___   ___  ______  _   _  _____  _____ 
  |_  | / _ \ | ___ \| | | ||_   _|/  ___|
    | |/ /_\ \| |_/ /| | | |  | |  \ `--. 
    | ||  _  ||    / | | | |  | |   `--. |
/\__/ /| | | || |\ \ \ \_/ / _| |_ /\__/ /
\____/ \_| |_/\_| \_| \___/  \___/ \____/ 
                                          
                                          


""")
time.sleep(1)
print("checking for not installed packages")
#comment out if you are not using arch
os.system("sudo pacman -Sy ollama kitty --noconfirm && yay -S cava freetube")
#os.system("sudo apt install cava ollama freetube kitty amixer")
print("creating the myjarvis module")
os.system("ollama create myjarvis -f jarvis.modelfile")
time.sleep(1)
print("checking for not installed pip packages...")

os.system("pip install asyncio subprocess os  faster_whisper edge_tts time sys sounddevice numpy tempfile wave colorama random")
time.sleep(1)
print("successfully installed all needet packages")
time.sleep(1)
print("Installation finished")
