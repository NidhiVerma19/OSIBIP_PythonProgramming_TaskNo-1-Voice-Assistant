from collections import deque
from datetime import datetime
import re
import webbrowser
import random
import os
import speech_recognition as sr
import pyttsx3

class Settings:
    RATE_WPM = 175
    LANGUAGE = "en-IN"
    MEMORY_SIZE = 5

class Speaker:
    def __init__(self, settings):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', settings.RATE_WPM)

    def speak(self, text):
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

class Listener:
    def __init__(self, settings):
        self.recognizer = sr.Recognizer()
        self.settings = settings

    def listen_once(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
            return self.recognizer.recognize_google(audio, language=self.settings.LANGUAGE).lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return "Sorry, I can't reach the speech service right now."

class VoiceAssistant:
    def __init__(self):
        self.settings = Settings()
        self.speaker = Speaker(self.settings)
        self.listener = Listener(self.settings)
        self.memory = deque(maxlen=self.settings.MEMORY_SIZE)

    def remember(self, user_text, assistant_text):
        self.memory.append((user_text, assistant_text))

    def casual_chat(self, text):
        responses = [
            "That's interesting! Tell me more.",
            "Hmm, I see.",
            "Why do you think that?",
            "I understand. What happened next?",
            "Haha, that's funny!",
            "Oh, really?",
            "I'm here to listen.",
            "That's nice to hear!"
        ]
        return random.choice(responses)

    def reply(self, text):
        if not text.strip():
            return "I didn't catch that. Could you repeat?"

        text = text.lower()

        qa_pairs = {
            "hello": "Hello! How can I help you today?",
            "hi": "Hello! How can I help you today?",
            "how are you": "I am good, how are you?",
            "what is your name": "My name is your friendly voice assistant.",
            "what's your name": "My name is your friendly voice assistant.",
        
        }

        for q, a in qa_pairs.items():
            if q in text:
                return a

        if "time" in text:
            return f"It's {datetime.now().strftime('%H:%M')}"
        elif "date" in text:
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
        elif text.startswith("open "):
            app = text.replace("open ", "").strip()
            if app:
                self.open_application(app)
                return f"Opening {app}"
            else:
                return "Which application should I open?"
        elif any(word in text for word in ["search", "google", "find", "look", "look for"]):
            query = re.sub(r"\b(search|google|find|look|look for)\b", "", text).strip()
            if query:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                return f"Searching Google for {query}"
            else:
                return "What should I search for?"
        elif "repeat that" in text and self.memory:
            return f"I said: {self.memory[-1][1]}"
        elif "what did i say" in text and self.memory:
            return f"You said: {self.memory[-1][0]}"
        elif "exit" in text or "quit" in text:
            return None
        else:
            return self.casual_chat(text)

    def open_application(self, app_name):
        if "spotify" in app_name:
            os.system("start spotify")
        elif "notepad" in app_name:
            os.system("notepad")
        elif "calculator" in app_name:
            os.system("calc")
        
        else:
            self.speaker.speak(f"I don't know how to open {app_name} yet.")

    def run(self):
        self.speaker.speak("Voice assistant ready. You can talk to me directly, or type in chat mode.")
        while True:
            mode = input("Type 'voice' to speak or 'chat' to type (or 'exit' to quit): ").strip().lower()
            if mode == 'voice':
                user_text = self.listener.listen_once()
                if not user_text:
                    self.speaker.speak("I didn't hear you. Please try again.")
                    continue
            elif mode == 'chat':
                user_text = input("You: ").strip().lower()
            elif mode == 'exit':
                self.speaker.speak("Goodbye!")
                break
            else:
                print("Invalid mode. Please type 'voice', 'chat', or 'exit'.")
                continue

            response = self.reply(user_text)
            if response is None:
                self.speaker.speak("Goodbye!")
                break

            self.speaker.speak(response)
            self.remember(user_text, response)

if __name__ == "__main__":
    VoiceAssistant().run()
