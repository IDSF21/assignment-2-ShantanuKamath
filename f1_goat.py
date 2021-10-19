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

st.title('Formula1')
st.title('Who is the GOAT - Greatest Of All Time')

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

data_load_state = st.text('Ready Set Lights')
data = load_data()
data_load_state.text('Ready Set Lights...done!')

subheading = st.subheader('Formula 1 - Race data from {}-{}'.format(1950, 2021))
year_values = st.slider('Select data range', 1950, 2021, (1950, 2021))
subheading.subheader('Formula 1 - Race data from {}-{}'.format(year_values[0], year_values[1]))

selected_options = st.multiselect("Select the drivers for comparison:", data.driver_name.unique(), ['Lewis Hamilton', 'Michael Schumacher', 'Nico Rosberg', 'Max Verstappen', 'Fernando Alonso'])

data = data[data.driver_name.isin(selected_options)]
data = data[data.race_year.between(year_values[0], year_values[1], inclusive=True)]
st.write(data)

resizedImages = []
cols = st.columns(len(selected_options))
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

cols = st.columns(len(selected_options))
for idx, name in enumerate(selected_options):
    wins = len(data[(data.driver_name == name) & (data.finish_position == 1)].index)
    podiums = len(data[(data.driver_name == name) & (data.finish_position.isin([1,2,3]))].index)
    poles = len(data[(data.driver_name == name) & (data.start_position.isin([1]))].index)
    total = len(data[(data.driver_name == name)].index)

    if total == 0:
        win_rate = 0
        podium_rate = 0
        pole_rate =  0
    else:
        win_rate = wins*100/total
        podium_rate = podiums*100/total
        pole_rate = poles*100/total
    cols[idx].metric(label="Race Win Rate", value="{:.2f} %".format(win_rate))
    cols[idx].metric(label="Podium Finish Rate", value="{:.2f} %".format(podium_rate))
    cols[idx].metric(label="Qualifying Pole Rate", value="{:.2f} %".format(pole_rate))
# map(data)
# if all_options:
#     selected_options = ['A', 'B', 'C']
# if un
# Win Percentage
# Map of wins per location
# Pole positions
# Most positions gained
