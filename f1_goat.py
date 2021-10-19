import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import http.client
import json
import requests
from PIL import Image
from io import BytesIO
st.set_page_config(layout="wide")

st.title('Formula1 - Greatest of all time')

@st.cache
def load_data():
    df = pd.read_csv("./race_results_mega.csv")
    return df

@st.cache
def get_driver_image(driver_name):
    driver_name = driver_name.replace(' ', '%20')
    conn = http.client.HTTPSConnection("api-formula-1.p.rapidapi.com")

    headers = {
        'x-rapidapi-host': "api-formula-1.p.rapidapi.com",
        'x-rapidapi-key': "7e627ff4bemsh076cf2f715b08f9p1ede64jsnb7e5375d9a8f"
        }

    conn.request("GET", "/drivers?search={}".format(driver_name), headers=headers)

    res = conn.getresponse()
    data = res.read()
    json_obj = json.loads(data.decode("utf-8"))
    if len(json_obj['response']) > 0:
        return json_obj['response'][0]['image']
    else:
        return "https://media.gettyimages.com/photos/racing-driver-standing-proud-on-black-background-picture-id91030097?k=20&m=91030097&s=612x612&w=0&h=tQI8woI99U7eEVCSwkrqJUUbcHpUIM41pLvZ856uXiY="

def map(data):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                auto_highlight=True,
                get_position=["lon", "lat"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))

data_load_state = st.text('Talking to all F1 Drivers...')
data = load_data()
data_load_state.text('Talking to all F1 Drivers......done!')

st.subheader('Formula 1 - Race data from 1950-2021')
# st.write(data)

selected_options = st.multiselect("Select one or more options:", data.driver_name.unique(), ['Lewis Hamilton', 'Michael Schumacher', 'Nico Rosberg', 'Max Verstappen', 'Fernando Alonso'])

data = data[data.driver_name.isin(selected_options)]
st.write(data)

resizedImages = []
cols = st.beta_columns(len(selected_options))
for idx, name in enumerate(selected_options):
    url = get_driver_image(name)
    try:
        r = requests.get(url)
        img = Image.open(BytesIO(r.content))
    except Exception as e:
        r = requests.get("https://media.gettyimages.com/photos/racing-driver-standing-proud-on-black-background-picture-id91030097?k=20&m=91030097&s=612x612&w=0&h=tQI8woI99U7eEVCSwkrqJUUbcHpUIM41pLvZ856uXiY=")
        img = Image.open(BytesIO(r.content))
    resizedImg = img.resize((225, 325), Image.ANTIALIAS)
    resizedImages.append(resizedImg)
    cols[idx].header(selected_options[idx])
    cols[idx].image(resizedImg)

# st.image(resizedImages, caption=selected_options)
# map(data)
# if all_options:
#     selected_options = ['A', 'B', 'C']
# if un
# Win Percentage
# Map of wins per location
# Pole positions
# Most positions gained
