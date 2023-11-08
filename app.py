import geocoder
import requests

# Retrieve users geolocation
geoloc = geocoder.ip('me')

user_lat = geoloc.lat
user_lon = geoloc.lng

print("User coordinates: " + str(user_lat) + ", " + str(user_lon))

# Parameters for retrieving weather forecast (latitude and longitude)
payload = {
    "lat": user_lat,
    "lon": user_lon
}

# URL for weather forecast API
weather_api_url = 'https://api.met.no/weatherapi/locationforecast/2.0/compact?'

response = requests.get(weather_api_url, params=payload)

if response.status_code != 200:
    print("Status code: " + str(response.status_code) + ". Something went wrong.")

response_json = response.json()

weather = response_json['properties']['timeseries'][1]['data']['instant']['details']

user_location = geoloc.city + ", " + geoloc.country
time = response_json['properties']['timeseries'][1]['time']
temperature = weather['air_temperature']
cloud_area_fraction = weather['cloud_area_fraction']
relative_humidity = weather['relative_humidity']
wind_speed = weather['wind_speed']

next_1_hour = response_json['properties']['timeseries'][1]['data']['next_1_hours']['summary']['symbol_code']

weather_description = "User location: " + user_location + "\nTime: " + str(time) + "\nTemperature: " + str(temperature)+ "\nCloud area fraction: " + str(cloud_area_fraction) + "\nRelative humidity: " + str(relative_humidity) + "\nWind speed: " + str(wind_speed) + "\nNext hour: " + next_1_hour

print(weather_description)

# OpenAI
from openai import OpenAI

client = OpenAI()

print(client.models.list())

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages= [
        {"role": "user", "content": "Say this is a test."}
    ]
)

print(completion.choices[0].message)