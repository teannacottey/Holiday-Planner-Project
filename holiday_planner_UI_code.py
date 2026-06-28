#import libraries 
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go  
import json

#import datasets 
nightlife_chart = pd.read_csv("data/nightlife/destinations_nightlife_data.csv")
weather_chart = pd.read_csv("data/weather/destinations_weather_agg_chart.csv")
flights_chart = pd.read_csv("data/flights/destinations_flights_agg_chart.csv")

#create destinations dictionary function 
def load_destinations(): 
    """
    Loads, merges, and converts destination CSV files into a 
    signle destination dictionary 
    """

    #list of destination files 
    folders = ['nightlife', 'weather', 'flights']

    dfs = {} #stores each df under it's folder name  

    #define file path
    for folder in folders: 
        file_path = f'data/{folder}/destinations_{folder}_agg.csv'
        dfs[folder] = pd.read_csv(file_path) #folder: file name

    #merge all dataframes on destination 
    merged = dfs['nightlife'] #first df to merge on 
    for folder in list(dfs.keys())[1:]: #locate each file by folder name 
        merged = merged.merge(dfs[folder], on='destination', how='inner')


    #merge validation - check for missing data 
    expected = 12 #number of destinations 
    if len(merged) < expected: 
        missing = expected - len(merged)
        print(f"Warning: {missing} destination(s) missing from files")
        print(f"Destinations loaded: {merged['destination'].tolist()}")
    else: 
        print(f"Destinations loaded: {merged['destination'].tolist()}")

    #convert merged df to a dictionary for scoring logic 
    destinations = {}
    for _, row in merged.iterrows(): #_ ignores the index 
        destinations[row['destination']] = { #destination name (row value) becomes outer dictionary key
            #key: row value  
            #nightlife cols 
            'country': row['country'], 
            'averageRating': row['averageRating'], 
            'totalReviews': row['totalReviews'], 
            #weather cols
            'maxTemperature': row['maxTemperature'],
            'sunshineHours': row['sunshineHours'],
            'precipitationHours': row['precipitationHours'],
            #flights cols 
            'flightPrice': row['average_price_gbp'], 
            'flightDuration': row['average_duration_hours']
        }

    return destinations

destinations = load_destinations()

#customer profiles dictionary 
profiles = {
     'The Budgeter': {
         'filters': {
             'flightPrice': ('<=', 500),
             'flightDuration': ('<=', 6)
         }, 
         'weights': {
             'averageRating': 0.4, 
             'flightPrice': 0.4, 
             'flightDuration': 0.2
         }
        }, 
    'The Party Seeker': {
        'filters': {},
        'weights': {
            'averageRating': 0.5, 
            'totalReviews': 0.2, 
            'sunshineHours': 0.3
        }
    }, 
    'The Beach Relaxer': {
        'filters': {
            'sunshineHours': ('>=', 9.5),
            'maxTemperature': ('>=', 23)
        },
        'weights': {
            'maxTemperature': 0.4, 
            'sunshineHours': 0.6
        }
    }
}

#destination score calculator  
def get_top_3(profile): 
    profile = profiles[profile] #extracts the full dictionary for selected profile
    pot_dests = [] #empty list of potential destinations 

    for dest, metrics in destinations.items(): #key(dest): values(metrics - dict)
        #apply filters first 
        eligible = True #destinations considered 
        for metric, (operator, threshold) in profile['filters'].items(): #checks through each filter
            value = metrics[metric] 
            if operator == '<=' and value > threshold:
                eligible = False #eliminates destination from consideration set
            elif operator == '>=' and value < threshold: 
                eligible = False
        if not eligible: 
            continue #moves on to next destination 

        #score destinations 
        score = 0.0 
        weights = profile['weights']

        #metrics where lower is better 
        lower_better = ['flightPrice','flightDuration']

        #score destinations based on weights         
        for metric, weight in weights.items():
            #list of all destination metric values for each metric 
            all_values = [metrics[metric] for metrics in destinations.values()]

            #normalise metric values 
            min_v, max_v = min(all_values), max(all_values)
            norm_v = (metrics[metric] - min_v) / (max_v - min_v) 

            if metric in lower_better: 
                norm_v = 1 - norm_v #flips score so lower values score higher

            #score updates every iteration 
            score += weight * norm_v #prioritises metrics with higher weights 

        pot_dests.append({'destination_name':dest, 'data': metrics, 'score': round(score * 10,2)})

    #return the top 3 destinations by score desc 
    return sorted(pot_dests, key=lambda x: x['score'], reverse=True)[:3]

#export recommendation results function
def export_results(top_3, profile):
    """
    Exports top 3 results to a JSON file for an AI written summary 
    """
    output = {
        'profile': profile,
        'recommendations': []
    }

    for result in top_3: 
        output['recommendations'].append({
            'destination': result['destination_name'], 
            'score': result['score'], 
            'data': result['data']
        })

    with open(f'recommendation_results({profile}).json', 'w') as file: 
        json.dump(output, file, indent=4) 

#reccomendations summary dictionary 
summaries = {
    'The Budgeter': {
        'Dubrovnik': """ Dubrovnik is your most affordable recommendation, with the lowest average monthly flight price of your top 3 at just £190.88
                and a flight duration of under 5 hours — ideal if you want to minimise travel costs and time. September to December brings cooler 
                temperatures of 19.1°C and 8.1 daily sunshine hours, but with only 4.0 average daily precipitation hours it's actually the driest 
                period of the year here, making it a surprisingly reliable choice. A nightlife rating of 4.55 across 9,507 reviews confirms there's 
                plenty to do once you arrive.""", 
        'Ibiza': """Ibiza offers the best weather of your budget top 3 during the September to December window, with 9.1 daily sunshine hours, 21.4°C, 
                and the second lowest precipitation average at just 2.7 hours — meaning you'll still catch plenty of sun despite the season. At an 
                average monthly flight price of £203.44 it remains an accessible option for budget-conscious travellers, and its nightlife rating of 
                4.45 across 16,014 reviews speaks to a well-established scene. While peak season crowds will have thinned by this point, the island 
                retains its energy well into autumn.""",
        'Mykonos': """Mykonos is the driest destination in your budget top 3, averaging just 1.8 daily precipitation hours between September and December
                — the lowest of all three profiles' recommendations. With 9.4 daily sunshine hours and temperatures of 21.1°C it offers the most 
                consistent sunshine of your top 3, though the £266.50 average monthly flight price is the highest of your budget recommendations. 
                Its extraordinary 32,715 nightlife reviews — the highest review count across all recommendations — confirm it as a world-renowned 
                destination that punches well above its price point."""}, 
    'The Party Seeker': {
        'Bali': """Bali's nightlife scene commands a 4.76 average rating across 13,089 reviews, making it your highest rated party destination and consistently beloved
                 by those who visit. September to December falls within Bali's rainy season, with 9.3 average daily precipitation hours — the highest of your top 3 — 
                 though the rain typically arrives in short tropical bursts that rarely disrupt the nightlife. At an average monthly flight price of £914.50 and a 
                 duration of nearly 20 hours it's the longest and most expensive journey of your recommendations, but for many the experience justifies the trip""",
        'Phuket': """ With the highest review count of your party top 3 at 23,371 and a nightlife rating of 4.79, Phuket is one of the most tried and tested party 
                destinations in the world. September to November sits within Phuket's monsoon season, reflected in 8.9 average daily precipitation hours, though temperatures
                remain a warm 29.7°C and Patong's legendary nightlife strip runs in full swing regardless of the weather. Average monthly flights come in at £727.50 
                with a journey time of around 16.5 hours, making it the mid-range option for both cost and travel time in your top 3.""",
        'Bangkok': """Bangkok earns the highest nightlife rating of your party top 3 at 4.81 across 10,112 reviews and is the most weather-resilient option during the 
                September to December period, averaging just 5.5 daily precipitation hours — the lowest of your recommendations. At £681.42 for an average monthly 
                flight and approximately 15.5 hours travel time, it's also your most accessible long-haul option. With rooftop bars, legendary club districts, and a 
                nightlife scene that thrives indoors, Bangkok delivers an unrivalled party experience at the best value of your top 3."""
    }, 
    'The Beach Relaxer': {
        'Holetown': """Holetown earns its top spot with the highest daily maximum temperature of your beach top 3 at 31.1°C and an outstanding 10.6 average sunshine 
                    hours per day. September to December falls within Barbados' Caribbean rainy season, averaging 7.2 daily precipitation hours, though showers here 
                    tend to be brief and tropical rather than day-long — leaving ample time on the beach. Average monthly flights come in at £724.08 with a journey of 
                    around 11.5 hours, making it the most time-efficient long-haul beach option in your recommendations.""", 
        'Cancun': """Cancún is your most weather-resilient beach destination during the September to December travel window, averaging the lowest daily precipitation 
                    hours of your beach top 3 at just 5.8 alongside 10.2 sunshine hours and a warm 29.5°C. While Mexico's Caribbean coast does experience its rainy season during 
                    this period, Cancún's figures suggest more consistent sunshine than your other recommendations. At £777.88 average monthly flight price and 15.4 hours travel 
                    time it's the longest journey of your beach top 3, but for guaranteed beach weather it's your safest bet.""",
        'Maldives': """The Maldives offers a comfortable 28.6°C and 10.3 daily sunshine hours, but September to December falls within the Maldivian wet season, 
                    reflected in 7.0 average daily precipitation hours — on par with Holetown. At £971.92 it carries the highest average monthly flight price across 
                    all three profiles' recommendations, with a journey time of around 12.8 hours. The unrivalled quality of the beaches, crystal clear waters, and 
                    the highest nightlife rating of your beach top 3 at 4.61 make it a worthy splurge for those who want the ultimate beach retreat."""
    }
}

#---------------------------------------------------- App UI ----------------------------------------------------------------

#app introduction
st.title('Holiday Planner App :beach_umbrella:')
st.write("Welcome to the Holiday Planner App! Get holiday ready with our data and AI-driven destination recommendations. ")
st.write("To get started, let us know what kind of traveller you are... 👀")
st.divider()

#customer profile - user input 
st.header("What type of traveller are you?")

#preference checkboxes 
profile = st.radio(
    "Let us know so we can give the best recommendations for you!", 
    ["The Budgeter", "The Party Seeker", "The Beach Relaxer"],
    captions=[
        "Value for money is your priority. You prefer affordable stays and good nightlife without breaking the bank.",
        "Nightlife is your priority. You prefer warm weather, lots of clubs and bars, and don’t mind travelling the extra mile.",
        "Nightlife isn’t the priority for you. You prefer sun, warmth, clear skies, and calm conditions."
    ]
)

if profile == "The Budgeter": 
    st.write(f"You have selected: {profile}")
    st.write("Nice! Who doesn't love a bit of budget-friendly fun.Getting your recommendations ready... :space_invader:")
if profile == "The Party Seeker": 
    st.write(f"You have selected: {profile}")
    st.write("Great Choice! A little partying never hurt anybody. Getting your recommendations ready... :space_invader:")
if profile == "The Beach Relaxer": 
    st.write(f"You have selected: {profile}")
    st.write("Lovely! Time to kick back and relax. Getting your recommendations ready... :space_invader:")

#top recommendations 
# provide top 3 recommendations based on selected profile
top_3 = get_top_3(profile)

#export resilts to json file 
#export_results(top_3, profile)

st.subheader(f"🏆 Top Recommendations for: {profile}")

for position, result in enumerate(top_3): 
    medal = ['🥇','🥈','🥉'][position] #medal given based on ranking position
    destination_name = result['destination_name']
    with st.expander(f"{medal} {result['destination_name']} - Score: {result['score']}/10", expanded=True):
        st.write("##### AI Summary")
        with st.container(border=True): #AI summary in here
            if profile in summaries and destination_name in summaries[profile]: 
                st.info(summaries[profile][destination_name])
            else: 
                st.warning('No summary available for this destination.')

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
with tab2: 
    #filter by selected destinations 
    filtered = flights_chart[flights_chart['destination'] == destination]

    #define month order for x axis 
    month_order = ['Sep','Oct','Nov','Dec']
    filtered['month'] = pd.Categorical(
        filtered['month'], categories = month_order, ordered = True
    )
    filtered = filtered.sort_values('month')

    #build weather chart 
    chart = go.Figure()

       #line 1 - flight price 
    chart.add_trace(go.Scatter(
        x = filtered['month'],
        y = filtered['average_price_gbp'], 
        name = 'Average Price', 
        mode = 'lines+markers', #graph annotation
        line=dict(color='#fc5f7c', width=2.5), 
        marker=dict(size=6)
    ))

    #populate weather chart
    chart.update_layout(
        title = f"{destination}'s End of Year Flights", 
        xaxis_title = 'Month', 
        yaxis_title = 'Value', 
        yaxis = dict(range = (0, 1300)), 
        legend = dict(orientation='h', yanchor = 'bottom', y=1.02, xanchor = 'right', x=1),
        hovermode = 'x unified', #shows all three values on hover together
        font = dict(size=12)
    )

    st.plotly_chart(chart)

    tab2.caption("*price is measured in pounds (£)\n \n*duration is measured in hours\n \n*flight metrics measure monthly averages")


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

#filter by selected destinations 
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
