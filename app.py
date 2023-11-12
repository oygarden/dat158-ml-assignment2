import PySimpleGUI as sg
import pickle
import os
import generate_wallpaper

sg.theme('Topanga')

# Check if OPENAI_API_KEY environment variable is set
if os.environ.get("OPENAI_API_KEY") is not None:
    api_key = os.environ.get("OPENAI_API_KEY")
else:
    api_key = ""

# Check if preference file exists
if os.path.isfile("preferences.pickle"):
    with open("preferences.pickle", "rb") as f:
        data = pickle.load(f)


else:
    # Define default preferences
    if not os.path.isdir(os.getcwd() + "\\images"):
        os.mkdir(os.getcwd() + "\\images")

    path = os.getcwd() + "\\images"

    data = {
        "FOLDER": path,
        "PREFERENCES": "",
        "UPDATE_INTERVAL": "2",  # In hours
        "QUALITY": "hd",
        "STYLE": "vivid",
        "OPENAI_API_KEY": api_key,
        "LOCATION_OVERRIDE": ""
    }

    with open("preferences.pickle", "wb") as f:
        pickle.dump(data, f)

    with open("preferences.pickle", "rb") as f:
        data = pickle.load(f)

window = sg.Window(
    title="Wallpaper Generator",
    layout=[
        [sg.Column([[sg.Text('Image Folder'), sg.In(size=(25, 1), enable_events=True, key='-FOLDER-', default_text=data["FOLDER"]),
                     sg.FolderBrowse(initial_folder=data["FOLDER"],)],[sg.Text('Image Preference'), sg.In(size=(25, 1), enable_events=True, key='-PREFERENCE-', default_text=data["PREFERENCES"])],
        [sg.Text('Location Override'), sg.In(size=(25, 1), enable_events=True, key='-LOCATION_OVERRIDE-', default_text=data["LOCATION_OVERRIDE"])],
        [sg.Text('OpenAI API Key'), sg.In(size=(25, 1), enable_events=True, key='-API_KEY-', default_text=data["OPENAI_API_KEY"])],
        [sg.Text('Quality'), sg.OptionMenu(values=['hd', 'standard'], default_value=data["QUALITY"], key='-QUALITY-')],
        [sg.Text('Style'), sg.OptionMenu(values=['vivid', 'natural'], default_value=data["STYLE"], key='-STYLE-')],
        [sg.Text('Update interval (hours)'), sg.Slider((1,24), default_value=data["UPDATE_INTERVAL"], orientation='h', key='-UPDATE_INTERVAL-', enable_events=True)],
        [sg.Button("Apply changes"), sg.Button("Generate wallpaper now"), sg.Button("Close")]], element_justification='c')],

    ],
    margins=(200, 100),
    resizable=True
)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Close'):
        break
    if event == 'Apply changes':

        # Make sure api key is set
        if data["OPENAI_API_KEY"] == "":
            sg.Popup("Please set OPENAI_API_KEY environment variable.")

        else:
            with open("preferences.pickle", "wb") as f:
                pickle.dump(data, f)

    if event == 'Generate wallpaper now':
        generate_wallpaper.main()


    if event == '-FOLDER-':
        data["FOLDER"] = values['-FOLDER-']

    if event == '-PREFERENCE-':
        data["PREFERENCES"] = values['-PREFERENCE-']

    if event == '-LOCATION_OVERRIDE-':
        data["LOCATION_OVERRIDE"] = values['-LOCATION_OVERRIDE-']

    if event == '-API_KEY-':
        data["OPENAI_API_KEY"] = values['-API_KEY-']

    if event == '-QUALITY-':
        data["QUALITY"] = values['-QUALITY-']

    if event == '-STYLE-':
        data["STYLE"] = values['-STYLE-']

    if event == '-UPDATE_INTERVAL-':
        data["UPDATE_INTERVAL"] = values['-UPDATE_INTERVAL-']


window.close()
