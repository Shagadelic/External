import pyttsx3
import datetime
import calendar as cal
import speech_recognition as sr
import wikipedia
import smtplib
import webbrowser as wb
import os

os.system("clear")

#setup speech 
engine = pyttsx3.init()
#speed
engine.setProperty("rate", 200)
rate = engine.getProperty("rate")

#outputs text as speach
def speak(audio):
    engine.say(audio)
    engine.runAndWait()
    engine.setProperty("voice", "english_rp+f3")

#tells time
def time_():
    time_var = datetime.datetime.now().strftime("%I:%M:%S")
    speak("The current time is")
    speak(time_var)

#tells date
def date_():
    
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day = datetime.datetime.now().weekday()
    speak("The current date is")
    speak("Year: "+ str(year))
    speak("Month: "+ str(cal.month_name[month]))
    speak("Day: "+ str(days[day]))

#tries to recognize a command
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as src:
        print("Listening..")
        r.pause_threshold = 1
        audio = r.listen(src)

    try:
        print("Recognizing..")
        query = r.recognize_google(audio, language = "en-US")
        print(query)
        return query

    except Exception as e:
        print(e)
        print("Please repeat that..")
        return None

#launches the specified application
def launch(query):
    try:
        os.system(query)
    except Exception as e:
        print(e)
        speak("Sorry, try again")


if __name__ == "__main__":

    while True:
        #lowercase commands for easier handling
        query = take_command().lower()

        if "time" in query:
            time_()
        if "date" in query:
            date_()
        elif "wikipedia" in query:
            speak("searching..")
            query = query.replace("wikipedia", "")
            result = wikipedia.summary(query, sentences=3)
            speak("According to wikipedia.:")
            print(result)
            speak(result)
        elif "launch" in query:
            query = query.replace("launch", "")
            launch(query)
        elif "google" in query:
            speak("Look for what?")
            search_Term = take_command().lower()
            wb.open("https://google.com/search?q="+search_Term)
        elif "quit" in query:
            speak("See ya, bye")
            quit()
