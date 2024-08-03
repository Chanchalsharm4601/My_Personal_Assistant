import speech_recognition as sr
import webbrowser
import pyttsx3
import musiclibrary
import requests
import google.generativeai as genai
import os
from transformers import pipeline

# Initialize recognizer and text-to-speech engine
r = sr.Recognizer()
engine = pyttsx3.init()

# # Debug: Print environment variables
# print(f"NEWS_API_KEY: {os.getenv('NEWS_API_KEY')}")
# print(f"GENAI_API_KEY: {os.getenv('GENAI_API_KEY')}")

# Read the API keys from environment variables
news_api_key = os.getenv("NEWS_API_KEY")
genai_api_key = os.getenv("GENAI_API_KEY")

# Ensure the keys are set before proceeding
if not news_api_key or not genai_api_key:
    raise ValueError("API keys are not set in the environment variables.")
else:
    print("Environment variables are set correctly.")  

# Configure the generative AI model
genai.configure(api_key=genai_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

voices = engine.getProperty('voices')
# for voice in voices:
#     print(f"Voice: {voice.name}")
#     print(f" - ID: {voice.id}")
#     print(f" - Languages: {voice.languages}")
#     print(f" - Gender: {voice.gender}")
#     print(f" - Age: {voice.age}\n")

engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 200)
engine.setProperty('volume', 1.5)

url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}'

headers = {
    'Authorization': f'Bearer {news_api_key}'
}

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


async def get_gemini_summary(query):
    response = model.generate_content(query)
    text_content = extract_text_from_response(response)
    summary = summarize_text(text_content)
    speak(summary)



async def extract_text_from_response(response):
    print("extracting text from response")
    if response and response.candidates:
        return response.candidates[0].content.parts[0].text
    return "Sorry, I couldn't get the information."

async def processCommand(c):
    c = c.lower().strip()  
    if c == "open google":
        webbrowser.open("https://google.com")
    elif c == "open facebook":
        webbrowser.open("https://www.facebook.com")
    elif c == "open linkedin":
        webbrowser.open("https://in.linkedin.com")
    elif c == "open youtube":
        webbrowser.open("https://www.youtube.com")
    elif c.startswith("play"):
        song = c.split(" ", 1)[1].strip()  
        print(f"Trying to play: '{song}'")  
        link = musiclibrary.music.get(song)
        if link:
            webbrowser.open(link)
        else:
            speak(f"Sorry, I could not find the song '{song}' in the music library.")
    elif "news" in c:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            articles = data['articles']
            for article in articles:
                title = article.get('title')
                if title:
                    speak(title)
        else:
            print(f"Failed to retrieve data: {response.status_code}")
    elif c:
        get_gemini_summary(c)
    else:
        speak("Command not recognized.")

async def summarize_text(text):
    summary = summarizer(text, max_length=100, min_length=20, do_sample=True)[0]["summary_text"]
    return summary

async def speak(text):
    engine.say(text)
    engine.runAndWait()

def stop_speech():
    engine.stop()


if __name__ == "__main__":
    speak("Initializing... ")
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source, timeout=10, phrase_time_limit=5)
            word = r.recognize_google(audio)
            print(f"Heard: {word}")  
            if word.lower() == "lucas":
                speak("Yes?")
                with sr.Microphone() as source:
                    print("lucas Active...")
                    audio = r.listen(source, timeout=10, phrase_time_limit=5)
                    command = r.recognize_google(audio)
                    print(f"Command: {command}")  
                    processCommand(command)
            elif word.lower() == "exit":
                speak("Shutting down.")
                break
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except Exception as e:
            print(f"An error occurred: {e}")