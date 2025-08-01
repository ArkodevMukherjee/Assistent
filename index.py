# Program Modules
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()

# Load LangChain model and tool decorator
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

# Speak function for text-to-speech
def speak(text):
    engine = pyttsx3.init("sapi5")
    engine.say(text)
    engine.runAndWait()
    engine.stop()

# Initialize the Gemini model
llm = init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Tools
@tool
def chromeApplication():
    """
    This tool opens the Chrome application for the user.
    """
    from AppOpener import open
    open("chrome", match_closest=True)
    return "Google Chrome opened from the laptop."

@tool
def firefox():
    """
    This tool opens the Firefox application for the user.
    """
    from AppOpener import open
    open("firefox", match_closest=True)
    return "Firefox opened from the laptop."

@tool
def dateTimeToolApp():
    """This tool helps to find out date and time for the user"""

    import datetime

    dateT = datetime.datetime.now()

    speak(f"Today week is {dateT.strftime("%A")}")
    speak(f"{dateT.strftime("%Y")}")
    speak(f"{dateT.strftime("%B")}")
    speak(f"Time is {dateT.strftime("%H")}")
    speak(f"{dateT.strftime("%M")}")

@tool
def openVSCodeAppTool():
    """This tool helps to open code editor from the laptop"""
    import os
    os.system("code")

# Bind tools to the model
llm = llm.bind_tools([chromeApplication, firefox,dateTimeToolApp,openVSCodeAppTool])

# Initialize speech recognizer
r = sr.Recognizer()

# Main interaction loop
while True:
    with sr.Microphone() as source:
        speak("What do you want to ask?")
        print("Listening...")

        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            text = r.recognize_google(audio)
            print(f"Recognized Text: {text}")
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand.")
            continue
        except sr.RequestError:
            speak("Speech recognition service is not available.")
            continue

        if text.lower() == "quit":
            break

        # Get model response
        data = llm.invoke(text)

        print("Model Response:", data)
        print("Tool Calls:", data.tool_calls)

        # Tool calling logic
        if data.tool_calls:
            tool_name = data.tool_calls[0]["name"]
            tool_args = data.tool_calls[0].get("args", {})
            print(f"Tool Name: {tool_name}")

            if tool_name == "chromeApplication":
                chromeApplication.invoke(tool_args)
                
            elif tool_name == "firefox":
                firefox.invoke(tool_args)

            elif tool_name == "dateTimeToolApp":
                dateTimeToolApp.invoke(tool_args)
                
            elif tool_name == "openVSCodeAppTool":
                openVSCodeAppTool.invoke(tool_args)

        # Speak the model's response
        if data.content:
            safe_text = re.sub(r'[^\x20-\x7E]+', ' ', data.content.strip())
            print("Speaking:", safe_text)
            speak(safe_text)