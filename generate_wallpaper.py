import geocoder
import requests
import os
import ctypes
import platform
import pickle
from datetime import datetime
from openai import OpenAI


# Retrieve users geolocation
def get_user_geoloc():
    geolocation = geocoder.ip("me")

    user_lat = geolocation.lat
    user_lon = geolocation.lng

    print("User coordinates: " + str(user_lat) + ", " + str(user_lon))

    return geolocation


# Retrieve weather description using MET Weather API
def get_weather_description(geoloc):
    # Retrieve coordinates from geolocation
    location_payload = {"lat": geoloc.lat, "lon": geoloc.lng}

    # URL for weather forecast API
    weather_api_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?"

    response = requests.get(weather_api_url, params=location_payload)

    if response.status_code != 200:
        print("Status code: " + str(response.status_code) + ". Something went wrong.")

    response_json = response.json()

    weather = response_json["properties"]["timeseries"][1]["data"]["instant"]["details"]

    user_location = geoloc.city + ", " + geoloc.country
    time = response_json["properties"]["timeseries"][1]["time"]
    temperature = weather["air_temperature"]
    cloud_area_fraction = weather["cloud_area_fraction"]
    relative_humidity = weather["relative_humidity"]
    wind_speed = weather["wind_speed"]

    next_1_hour = response_json["properties"]["timeseries"][1]["data"]["next_1_hours"][
        "summary"
    ]["symbol_code"]

    weather_string = (
        "User location: "
        + user_location
        + "\nTime: "
        + str(time)
        + "\nTemperature: "
        + str(temperature)
        + "\nCloud area fraction: "
        + str(cloud_area_fraction)
        + "\nRelative humidity: "
        + str(relative_humidity)
        + "\nWind speed: "
        + str(wind_speed)
        + "\nDescription: "
        + next_1_hour
    )

    print(weather_string)

    return weather_string


# OpenAI
# Define function for generating prompt for image generation using OpenAI API
def generate_prompt(weather_description, user_preferences):
    # API call for generating descriptive prompt for generation of wallpaper
    client = OpenAI()

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You generate a detailed description of the general atmosphere based on the weather "
                "forecast, location and user preferences to be used in image generation in 200 characters "
                "or less. Specify style and content of the image of your own choosing.",
            },
            {
                "role": "user",
                "content": "%s %s" % (weather_description, user_preferences),
            },
        ],
    )

    generated_prompt = chat_completion.choices[0].message.content

    print(generated_prompt)

    return generated_prompt


def generate_image(image_prompt, quality, style, save_directory):
    client = OpenAI()

    # API call for generating wallpaper using dall-e-3 model
    image_completion = client.images.generate(
        model="dall-e-3",
        prompt=image_prompt,
        size="1792x1024",
        quality=quality,
        style=style,
        n=1,
    )

    # Retrieve image URL from API response
    image_url = image_completion.data[0].url

    # Download image
    image = requests.get(image_url)

    # Create image name based on current date and time
    image_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".png"

    # If directory does not exist, create it
    if not os.path.isdir(save_directory):
        os.mkdir(save_directory)

    # Define image path
    image_path = os.path.join(save_directory, image_name)

    print(image_path)

    if image.status_code == 200:
        with open(image_path, "wb") as image_file:
            image_file.write(image.content)
            image_file.close()
            print(f"Image was saved as {image_name} in {save_directory} directory.")

    return image_path


# Set wallpaper
def set_wallpaper(image_path):
    system = platform.system().lower()

    path = image_path

    if system == "windows":
        # BOOL SystemParametersInfoW(
        #    UINT  uiAction,            # 20 -> SPI_SETDESKWALLPAPER = set desktop wallpaper
        #    UINT  uiParam,
        #    PVOID pvParam,             # Path to image
        #    UINT  fWinIni              # 3 -> SPIF_SENDWININICHANGE = Save update
        # );
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)

    print("Wallpaper was set.")


# Main function
def main():
    # Load preferences
    with open("preferences.pickle", "rb") as f:
        data = pickle.load(f)

    geoloc = get_user_geoloc()

    # Check if location override is set
    if data["LOCATION_OVERRIDE"] != "":
        geoloc = geocoder.osm(data["LOCATION_OVERRIDE"])

    weather_description = get_weather_description(geoloc)

    user_preferences = data["PREFERENCES"]

    # Generate a prompt based on weather description and user preferences
    prompt = generate_prompt(weather_description, user_preferences)

    # Generate image
    image_path = generate_image(prompt, data["QUALITY"], data["STYLE"], data["FOLDER"])

    # Set the generated image as desktop wallpaper
    set_wallpaper(image_path)



