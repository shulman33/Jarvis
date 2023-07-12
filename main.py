import openai
import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import tempfile
from gtts import gTTS
import os
import pvporcupine
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from pvrecorder import PvRecorder
import requests
import geocoder
from dotenv import load_dotenv


class VoiceAssistant:
    """
    This class represents a voice assistant.

    Attributes:
        history (list): A list of dictionaries representing the assistant's history.

    Methods:
        listen: Records audio from the user and transcribes it.
        think: Generates a response to the user's input.
        speak: Converts text to speech and plays it.
    """

    def __init__(self):
        load_dotenv()

        openai.api_key = os.getenv('OPENAI_KEY')
        spotify_secret = os.getenv('SPOTIFY_SECRET')

        # Initialize the assistant's history
        self.history = [
            {"role": "system", "content": "You are a helpful assistant. The user is english. Only speak english."}
        ]

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="5fad2c1d19a04ace8faea9ebfef72f4d",
                                                       client_secret=spotify_secret,
                                                       redirect_uri="https://www.samjshulman.com/",
                                                       scope="user-modify-playback-state user-read-playback-state"))

    def get_weather(self):

        weather_key = os.getenv('WEATHER_KEY')

        g = geocoder.ip('me')
        print(g.latlng)
        latitude = g.latlng[0]
        longitude = g.latlng[1]
        latlong = str(latitude) + "," + str(longitude)

        url = "https://api.weatherapi.com/v1/current.json?key=" + weather_key + "&q=" + latlong
        print(url)

        response = requests.get(url)

        return {
            "city": response.json()['location']['name'],
            "state": response.json()['location']['region'],
            "temperature": response.json()['current']['temp_f'],
        }

    def play_spotify_playlist(self, playlist_name):

        # Get the user's playlists
        playlists = self.sp.current_user_playlists()

        devices = self.sp.devices()
        device_id = devices['devices'][0]['id']
        print(devices)
        print(device_id)

        for playlist in playlists['items']:
            if playlist['name'].lower() == playlist_name.lower():
                self.sp.start_playback(context_uri=playlist['uri'], device_id=device_id)
                break

    def pause_music(self):

        self.sp.pause_playback()

    def play_next_song(self):

        self.sp.next_track()

    def play_music(self):

        self.sp.start_playback()

    def listen(self):
        """
        Continually records audio from the user and transcribes it.
        When the trigger phrase is heard, the command that follows the trigger phrase is returned.
        """

        porcupine = pvporcupine.create(
            access_key="K3wKsQn/chvZwrrXb6D/vEesCHZdfTITVpMs16vfgrSNi5RrKyV4qA==",
            keywords=["jarvis"])

        recoder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

        try:
            recoder.start()

            while True:
                keyword_index = porcupine.process(recoder.read())
                if keyword_index >= 0:
                    print("Keyword Detected")
                    print("Listening...")
                    duration = 3
                    fs = 44100  # Sample rate

                    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.int16)
                    sd.wait()

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
                        wavfile.write(temp_wav_file.name, fs, audio)

                        transcript = openai.Audio.transcribe("whisper-1", temp_wav_file)

                    print(f"User: {transcript['text']}")
                    return transcript['text']

        except KeyboardInterrupt:
            recoder.stop()
        finally:
            porcupine.delete()
            recoder.delete()

    def think(self, text):
        """
        Generates a response to the user's input.
        """
        # Add the user's input to the assistant's history
        self.history.append({"role": "user", "content": text})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.history,
            temperature=0.5
        )
        # Extract the assistant's response from the API response
        message = dict(response.choices[0])['message']['content']
        self.history.append({"role": "system", "content": message})
        print('Assistant: ', message)
        return message

    def speak(self, text):
        """"
        Converts text to speech and plays it.
        """
        tts = gTTS(text=text, lang='en')
        filename = "voice.mp3"
        tts.save(filename)
        playback_speed = 1.5
        os.system(f"afplay {filename} -r {playback_speed}")

        # remove the file after playing
        os.remove(filename)


if __name__ == "__main__":

    assistant = VoiceAssistant()

    while True:
        text = assistant.listen()

        if "goodbye" in text.strip().lower():
            print("Assistant: Goodbye! Have a great day!")
            assistant.speak("Goodbye! Have a great day!")
            break

        elif "playlist" in text.strip().lower():
            playlist = text.strip().lower().split("playlist")[0].split()[-1]
            print(type(playlist))
            print("Assistant: Playing playlist!")
            assistant.speak("playing your " + playlist + " playlist")
            assistant.play_spotify_playlist(playlist)

        elif "pause the music" in text.strip().lower():
            assistant.pause_music()

        elif "play music" in text.strip().lower():
            assistant.play_music()

        elif "next song" in text.strip().lower():
            assistant.play_next_song()

        elif "weather" in text.strip().lower():
            weather = assistant.get_weather()
            print(weather)
            assistant.speak("The weather in " + weather['city'] + weather['state'] + " is " + str(weather['temperature']) + " degrees fahrenheit")

        else:
            response = assistant.think(text)
            assistant.speak(response)

