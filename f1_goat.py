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

st.text('No way to settle an argument...')
st.text('Tired of always arguing with your friends...')
st.text("Not being able to convince them that you're right...")
st.text("Well this should help you!")
st.title('Who is the Formula 1 GOAT (Greatest Of All Time) ?')
st.text('And now I can argue (or not) with facts. Yes facts. Not just anecdotes and glamour, but cold hard FACTS.')

flag=False
@st.cache
def load_data():
    return pd.read_csv("./race_results_mega.csv")

@st.cache
def get_driver_image(driver_name):
    driver_name = driver_name.replace(' ', '%20')
    conn = http.client.HTTPSConnection("api-formula-1.p.rapidapi.com")
        # 'x-rapidapi-key': "7e627ff4bemsh076cf2f715b08f9p1ede64jsnb7e5375d9a8f"

    headers = {
        'x-rapidapi-host': "api-formula-1.p.rapidapi.com",
        'x-rapidapi-key': st.secrets["rapidapi_key"]
        # 'x-rapidapi-key': "7e627ff4bemsh076cf2f715b08f9p1ede64jsnb7e5375d9a8f"
        }

    conn.request("GET", "/drivers?search={}".format(driver_name), headers=headers)

    res = conn.getresponse()
    data = res.read()
    json_obj = json.loads(data.decode("utf-8"))
    if len(json_obj['response']) > 0:
        return json_obj['response'][0]['image']
    else:
        return "https://media.gettyimages.com/photos/racing-driver-standing-proud-on-black-background-picture-id91030097?k=20&m=91030097&s=612x612&w=0&h=tQI8woI99U7eEVCSwkrqJUUbcHpUIM41pLvZ856uXiY="

def map(data, lat, lon, zoom, column):
    column.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mapbox/light-v9',
     initial_view_state=pdk.ViewState(
         latitude=lat,
         longitude=lon,
         zoom=zoom,
         pitch=50,
     ),
     layers=[
         pdk.Layer(
            'HexagonLayer',
            data=data,
            get_position='[lon, lat]',
            radius=100,
            elevation_scale=4,
            elevation_range=[0, 100],
            pickable=True,
            extruded=True,
         )
     ],
 ))

def winner():
    flag=True
    st.balloons()
    col3.title("Lewis Hamilton")
    col3.image(resizedImgs[0])

def calculate_scores(scores):
    max_val = max(scores)
    for idx, val in enumerate(scores):
        total_scores[idx] += val/max_val*100

# Load Data
# data_load_state = st.subheader('Calling Hamilton, Schumacher and Alonso, asking for their stats...')
data = load_data()
# data_load_state.subheader('Calling Hamilton, Schumacher and Alonso, asking for their stats...and done!')


# Query Date Range
subheading = st.subheader('Race data from {}-{}'.format(1950, 2021))
year_values = st.slider('Select data range', 1950, 2021, (1950, 2021))
subheading.subheader('Race data from {}-{}'.format(year_values[0], year_values[1]))

# Query Drivers
st.subheader('Select drivers')
# ['Lewis Hamilton', 'Michael Schumacher', 'Kimi Raikkonen', 'Fernando Alonso']
selected_drivers = st.multiselect("Select the drivers for comparison:", data.driver_name.unique(), ['Nico Rosberg','Kimi Raikkonen', 'Fernando Alonso'])
data = data[data.driver_name.isin(selected_drivers)]
data = data[data.race_year.between(year_values[0], year_values[1], inclusive=True)]

# Display Dataset
st.write(data)

# Display driver image
resizedImgs = []
total_scores = [0 for _ in selected_drivers]

cols = st.columns(len(selected_drivers))
for idx, name in enumerate(selected_drivers):
    url = get_driver_image(name)
    try:
        r = requests.get(url)
        img = Image.open(BytesIO(r.content))
    except Exception as e:
        r = requests.get("https://media.gettyimages.com/photos/racing-driver-standing-proud-on-black-background-picture-id91030097?k=20&m=91030097&s=612x612&w=0&h=tQI8woI99U7eEVCSwkrqJUUbcHpUIM41pLvZ856uXiY=")
        img = Image.open(BytesIO(r.content))
    resizedImg = img.resize((225, 325), Image.ANTIALIAS)
    cols[idx].header(selected_drivers[idx])
    cols[idx].image(resizedImg)
    resizedImgs.append(resizedImg)

# Statistics
cols = st.columns(len(selected_drivers))
win_rates, podium_rates, pole_rates = [], [], []
for idx, name in enumerate(selected_drivers):
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
    win_rates.append(win_rate)
    podium_rates.append(podium_rate)
    pole_rates.append(pole_rate)

# calculate_scores(win_rates)
calculate_scores(podium_rates)
calculate_scores(pole_rates)

# Select circuits
st.subheader("Select your favourite circuit")
selected_circuit = st.selectbox("Select a race circuits for comparison:", data.circuit_name.unique(), index=7)
cols = st.columns(len(selected_drivers))

# Display circuits
win_rates = []
points = []
avg_points = []

cols = st.columns(len(selected_drivers))
for idx, name in enumerate(selected_drivers):
    driver_data = data[(data.driver_name == name)]
    lat = data[data.circuit_name == selected_circuit].lat.iloc[0]
    lon = data[data.circuit_name == selected_circuit].lon.iloc[0]
    cols[idx].header(selected_circuit)
    map(driver_data,lat, lon, 15    , cols[idx])
    race_data = driver_data[driver_data.circuit_name == selected_circuit].set_index('race_year')
    race_data.index = race_data.index.map(str)
    race_data['position_gained'] = race_data['finish_position'] - race_data['start_position']
    cols[idx].subheader('Positions')
    cols[idx].line_chart(race_data[['start_position', 'finish_position', 'position_gained']])
    total_points = race_data['points'].sum()
    wins = len(race_data[race_data['finish_position']== 1])
    avg_point = race_data['points'].mean()
    delta = race_data[race_data.index == race_data.index[-1]]['points'].mean()
    cols[idx].metric(label="Wins on this circuit", value="{}".format(wins))
    cols[idx].metric(label="Total Points earned on this circuit", value="{}".format(total_points), delta=delta)
    cols[idx].metric(label="Average points earned per race", value="{:.1f}".format(avg_point))
    win_rates.append(win_rate)
    points.append(total_points)
    avg_points.append(avg_point)

calculate_scores(win_rates)
calculate_scores(points)
calculate_scores(avg_points)

idx = total_scores.index(max(total_scores))
_, col3, _ = st.columns([1,1,1])
col3.subheader("And the GOAT (Based on the arbitrary scoring) is...")
col3.title(selected_drivers[idx])
col3.image(resizedImgs[idx])
col3.button("Celebrate!", on_click=st.balloons)
