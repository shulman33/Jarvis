import requests
import geocoder
import os
from dotenv import load_dotenv

class Weather:
    def __init__(self):
        load_dotenv()
        self.weather_key = os.getenv('WEATHER_KEY')

    def get_weather(self):
        g = geocoder.ip('me')
        latitude = g.latlng[0]
        longitude = g.latlng[1]
        latlong = str(latitude) + "," + str(longitude)

        url = "https://api.weatherapi.com/v1/current.json?key=" + self.weather_key + "&q=" + latlong

        response = requests.get(url)

        return {
            "city": response.json()['location']['name'],
            "state": response.json()['location']['region'],
            "temperature": response.json()['current']['temp_f'],
        }
