import pyttsx3

def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)     # Speed
    engine.setProperty('volume', 1.0)   # Volume
    engine.say(text)
    engine.runAndWait()
