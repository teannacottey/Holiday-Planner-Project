#import libraries 

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go 
#from destinations_data_merged.ipynb import load_destinations

#import datasets 
#destinations = load_destinations()
nightlife_chart = pd.read_csv("data/nightlife/destinations_nightlife_data.csv")
weather_chart = pd.read_csv("data/weather/destinations_weather_agg_chart.csv")
#flights_chart = pd.read_csv("data/flights/destinations_flights_agg_chart.csv")

#app introduction
st.title('Holiday Planner App :beach_umbrella:')
st.write("Welcome to the Holiday Planner App! Get holiday ready with our data and AI-driven destination recommendations.")
st.write("To get started, let us know what kind of traveller you are...")
st.divider()

#customer profile - user input 
st.header("What type of traveller are you?")

#customer profiles - DICTIONARY 


#preference checkboxes 
profile = st.radio(
    "Let us know so we can give the best recommendations for you!", 
    ["**:money_with_wings: The Budgeter**", "**:partying: The Party Seeker**", "**:gem: The Luxury Traveller**", "**:beach_umbrella: The Beach Relaxer**"],
    captions=[
        "Value for money is your priority. You prefer affordable stays and good nightlife without breaking the bank.",
        "Nightlife is your priority. You prefer warm weather, lots of clubs and bars, and don’t mind travelling the extra mile.",
        "Comfort and exclusivity are your priority. You prefer fine dining, high-end hotels, and warm and clear weather.",
        "Nightlife isn’t the priority for you. You prefer sun, warmth, clear skies, and calm conditions."
    ]
)

#destination score calculator - 


if profile == "**profile1**": 
    st.write(f"You have selected: {profile}")
    st.write("Nice! Who doesn't need a bit of... Your recommendations are ready!")
if profile == "**profile2**": 
    st.write(f"You have selected: {profile}")
    st.write("Nice! Who doesn't need a bit of... Your recommendations are ready!")
if profile == "**profile3**": 
    st.write(f"You have selected: {profile}")
    st.write("Nice! Who doesn't need a bit of... Your recommendations are ready!")
if profile == "**profile4**": 
    st.write(f"You have selected: {profile}")
    st.write("Nice! Who doesn't need a bit of... Your recommendations are ready!")

st.subheader("Top Recommendations:")

#top recommendations 
# provide top 3 recommendations based on selected profile
#copy profile selection if code to set recommendation conditions

#design - numbered boxes + name + desc + map/picture 

cols = st.columns(3) 

#for loop to create containiners with image, name and description 
for col in cols: 
    with col:
        st.container(border=True)

#LLM 
st.write("##### AI Summary")
st.container(border=True) #AI summary in here

#interactive graphs - detailed exploration of destinations 
st.divider()
st.header("Destinations Deep Dive")
st.write("Want to see the what makes these destinations perfect for you or interested in other possible destinations? Explore the graphs below.")

#filter by selected destination 
#change destination with df destination columns - df["destination"]
destination = st.selectbox("Filter graphs by destination", ["Tenerife", "Ibiza", "Mykonos", "Cancun", "Bali", "Bangkok", "Maldives", "Phuket", "Holetown", "Sal", "Dubrovnik", "Miami"])

#graphs 
st.subheader("Destination Charts")
st.write("Select your desired tab to view more information about your selected destination.")

tab1, tab2, tab3 = st.tabs([f"{destination} Weather", f"{destination} Flights", f"{destination} Nightlife"])

#weather graph 
tab1.write(f"##### {destination} Weather")
tab1.write(f"Explore {destination}'s end-of-year weather conditions: ")
#create graph inside tab 1 
with tab1: 
    #filter by selected destinations 
    filtered = weather_chart[weather_chart['destination'] == destination]

    #define month order for x axis 
    month_order = ['Sep','Oct','Nov','Dec']
    filtered['month'] = pd.Categorical(
        filtered['month'], categories = month_order, ordered = True
    )
    filtered = filtered.sort_values('month')

    #build weather chart 
    chart = go.Figure()

    #line 1 - max tempurature 
    chart.add_trace(go.Scatter(
        x = filtered['month'],
        y = filtered['maxTemperature'], 
        name = 'Max Temp (ºC)', 
        mode = 'lines+markers', #graph annotation
        line=dict(color='#fc5f7c', width=2.5), 
        marker=dict(size=6)
    ))

    #line 2 - sunshine hours 
    chart.add_trace(go.Scatter(
        x = filtered['month'],
        y = filtered['sunshineHours'], 
        name = 'Sunshine Hours', 
        mode = 'lines+markers', #graph annotation
        line=dict(color='#fefdd2', width=2.5), 
        marker=dict(size=6)
    ))

    #line 3 -  precipitation hours 
    chart.add_trace(go.Scatter(
        x = filtered['month'],
        y = filtered['precipitationHours'], 
        name = 'Precipitation Hours', 
        mode = 'lines+markers', #graph annotation
        line=dict(color='#6869fd', width=2.5), 
        marker=dict(size=6)
    ))

    #populate weather chart
    chart.update_layout(
        title = f"{destination}'s End of Year Weather", 
        xaxis_title = 'Month', 
        yaxis_title = 'Value', 
        yaxis = dict(range = (0, 36)), 
        legend = dict(orientation='h', yanchor = 'bottom', y=1.02, xanchor = 'right', x=1),
        hovermode = 'x unified', #shows all three values on hover together
        font = dict(size=12)
    )

    st.plotly_chart(chart)

    tab1.caption("*maxTemperature is measured in celcius\n \n*weather metrics measure daily averages")


#flights graph - ADD FLIGHTS (COPY CODE ABOVE) 
tab2.write(f"##### {destination} Flights")
tab2.write(f"Explore {destination}'s end-of-year flight prices: ")
#create graph inside tab2  
tab2.caption("*price is measured in pounds (£)\n  \n*flight metrics measure... averages")

#flight graph 2 ?? - corr - flight price vs duration 

#nightlife table 
tab3.write(f"##### {destination} Nightlife")
tab3.write(f"Explore {destination}'s top nightlife spots: ")

with tab3: 
    #filter by selected destinations 
    filtered = nightlife_chart[nightlife_chart['destination'] == destination]

    st.dataframe(data=filtered, hide_index=True)

    tab3.caption("*totalScore refers to the location rating\n  \n*reviewsCount measures the total number of reviews")


#heatmap - restaurant, bar, nightclubs density by destination 
st.subheader("Nightlife by Destination")
st.write("This heatmap highlights the nightlife available across each destination.")

#allow comparison between destinations
destination = st.multiselect("Compare Desination's Nightlife:", ["Tenerife", "Ibiza", "Mykonos", "Cancun", "Bali", "Bangkok", "Maldives", "Phuket", "Holetown", "Sal", "Dubrovnik", "Miami"])

#filter by selected destinations - FIX
filtered = nightlife_chart[nightlife_chart['destination'].isin(destination)]

#pivot nighlife data to count venues per category 
heatmap_df = filtered.pivot_table(
    index='destination',
    columns='category', 
    values='title', 
    aggfunc = 'count',
    fill_value=0
)

#create heatmap
map = go.Figure(data=go.Heatmap(
    z=heatmap_df.values, #counts
    x=heatmap_df.columns.tolist(), #category names
    y=heatmap_df.index.tolist(), #destination names 
    colorscale = 'Purples',
    text = heatmap_df.values, 
    textfont = dict(size=12)
))

#populate heatmap
map.update_layout(
    title = 'Nightlife Spots Density by Destination',
    xaxis_title = 'Category', 
    yaxis_title = 'Destination', 
    xaxis = dict(side='bottom'), 
    margin = dict(l=120, r=40, t=60, b=40)
)

st.plotly_chart(map)
st.caption("*This data does not cover all available nightlife spots in each destination, counts are reflective of the gathered data (top nightlife spots on google maps) not absolute values.")