# spotify.py
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

class Spotify:
    def __init__(self):
        load_dotenv()
        spotify_secret = os.getenv('SPOTIFY_SECRET')

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="5fad2c1d19a04ace8faea9ebfef72f4d",
                                                       client_secret=spotify_secret,
                                                       redirect_uri="https://www.samjshulman.com/",
                                                       scope="user-modify-playback-state user-read-playback-state"))

    def play_spotify_playlist(self, playlist_name):
        playlists = self.sp.current_user_playlists()

        devices = self.sp.devices()
        device_id = devices['devices'][0]['id']

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
