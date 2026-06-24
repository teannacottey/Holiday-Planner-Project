#import libraries 

import streamlit as st
import pandas as pd
import numpy as np

#app introduction
st.title('Holiday Planner App :beach_umbrella:')
st.write("Welcome to the Holiday Planner App! Get holiday ready with our data-driven, AI destination recommendations.")
st.write("To get started, let us know what kind of traveller you are...")
st.divider()

#customer profile - user input 
st.header("What type of traveller are you?")

#customer profiles 


#preference checkboxes - DEFINE PROFILES 
profile = st.radio(
    "Let us know so we can give the best recommendations for you!", 
    ["**profile1**", "**profile2**", "**profile3**", "**profile4**"],
    captions=[
        "profile1 characteristics",
        "profile2 characteristics",
        "profile3 characteristics",
        "profile4 characteristics"
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

#filter by selected country 
#change country with df country columns - df["country"]
country = st.selectbox("Filter graphs by destination", ["country1", "country2"])

#graphs 
st.subheader("Destination Charts...")
st.write("Select your desired tab to view more information about your selected country.")

tab1, tab2, tab3 = st.tabs(["Chart 1", "Chart 2", "Chart 3"])

tab1.write(f"##### {country}: Chart 1")
tab2.write(f"##### {country}: Chart 2")
tab3.write(f"##### {country}: Chart 3")

#if country = ... graph =....
#filter df columns used in chart by user input 

#heatmap - restaurant, bar, nightclubs density by city 
st.subheader(f"{country}: Nightlife by City")
st.write("This heatmap highlights the cities in your selected country with the most nightlife available.")

#if country = ... graph =....
#filter df columns used in chart by user input 

 #import plotly.figure_factory as ff 
 #x= df[["restuarants", "bars", "nightlife"]]
 #y = df["cities"]
 #fig = ff.create_annotated_heatmap(df, x=x, y=y,colorscale="")
 #st.plotly_chart(fig)

 #raw data filtered by country selection 
st.subheader("Raw Destination Data")
st.write("This table displays more detailed information about your selected country.")
st.dataframe(data=None) #replace with destination data
