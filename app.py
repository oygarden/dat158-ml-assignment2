import geocoder
import requests
import os
from datetime import datetime

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

weather_description = "User location: " + user_location + "\nTime: " + str(time) + "\nTemperature: " + str(temperature)+ "\nCloud area fraction: " + str(cloud_area_fraction) + "\nRelative humidity: " + str(relative_humidity) + "\nWind speed: " + str(wind_speed) + "\nDescription: " + next_1_hour

print(weather_description)

# The user should be able to specify the style of the image to be generated
user_preferences = "\nStyle: " + "Vincent van Gogh"


# OpenAI
from openai import OpenAI

client = OpenAI()

#API call for generating descriptive prompt for generation of wallpaper
chat_completion = client.chat.completions.create(
   model="gpt-3.5-turbo",
   messages= [
       {"role":"system", "content":"You generate a detailed description of the general atmosphere based on the weather forecast, location and user preferences to be used in image generation in 200 characters or less. Specify style and content of the image of your own choosing."},
       {"role": "user", "content": "%s %s" % (weather_description, user_preferences)}
   ]
)

# Retrieve prompt from API response
prompt = chat_completion.choices[0].message.content
print(prompt)

# API call for generating wallpaper using dall-e-3 model
image_completion = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1792x1024",
    quality="standard",
    n=1,
)

# Retrieve image URL from API response
image_url = image_completion.data[0].url

# Download image
image = requests.get(image_url)

# Define save directory
save_directory_name = "images"
save_directory = os.path.join(os.curdir, save_directory_name)

# Create image name based on current date and time
image_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".png"

# If directory does not exist, create it
if not os.path.isdir(save_directory):
    os.mkdir(save_directory)

# Define image path
image_path = os.path.join(save_directory, image_name)

if image.status_code == 200:

    with open(image_path, "wb") as image_file:
        image_file.write(image.content)
        image_file.close()
        print(f'Image was saved as {image_name} in {save_directory_name} directory.')



# Set wallpaper
import os
import ctypes
import platform

def set_wallpaper(image_name):
    system = platform.system().lower()

    path = ''

    if system == 'windows':
        path = os.getcwd() + '\\images\\' + image_name


        # BOOL SystemParametersInfoW(
        #    UINT  uiAction,
        #    UINT  uiParam,
        #    PVOID pvParam,
        #    UINT  fWinIni
        # );
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)

set_wallpaper(image_name)