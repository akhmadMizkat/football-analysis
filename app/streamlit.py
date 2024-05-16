import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from sklearn.preprocessing import Normalizer
import json
# from fbprophet import Prophet
# Set page configuration
# Define the pages
st.set_page_config(layout="centered")
pages = ["Head to Head", "Team Analysis", "Player Analysis"]

# Create a dropdown menu in the sidebar to select the page
selected_page = st.sidebar.selectbox('Select a page', pages)

def head_to_head():
    st.header("Head to Head")
    # Add your code for the Head to Head page here

def team_analysis():

    # Fetch the team names from the API
    all_team = requests.get('http://localhost:5000/all_teams')
    team_names = all_team.json()

    # Create a dropdown menu with the team names
    selected_team = st.selectbox('Select a team', team_names)
    # Fetch data from the endpoint
    response = requests.get(f'http://localhost:5000/team?team_name={selected_team}')
    data = response.json()

    # Create columns for team name and badge
    col1, col2 = st.columns([0.2, 0.9])

    # Display team badge in the first column
    with col1:
        st.image(data['team_badge'])

    # Display team name in the second column
    with col2:
        st.title(data['team_name'])

    # Create columns for founded, venue, coach, and position
    col3, col4, col5, col6 = st.columns(4)

    # Display founded in the first column of the second row
    with col3:
        st.subheader('Founded')
        st.write(data['team_founded'])

    # Display venue in the second column of the second row
    with col4:
        st.subheader('Venue')
        st.write(data['venue_name'])

    # Display coach in the third column of the second row
    with col5:
        st.subheader('Coach')
        st.write(data['coach_name'])

    # Display position in the fourth column of the second row
    with col6:
        st.subheader('Position')
        st.write(data['overall_league_position'])
    #League Stats

    st.subheader('League Stats')
    # Create a DataFrame for the bar chart
    df = pd.DataFrame({
        'Type': ['Wins', 'Draws', 'Losses'],
        'Count': [int(data['overall_league_W']), int(data['overall_league_D']), int(data['overall_league_L'])]
    })

    # Create a horizontal bar chart
    st.bar_chart(df.set_index('Type'))

    # Create two new columns
    col7, col8 = st.columns(2)

    # Home Stats
    with col7:
        st.subheader('Home Stats')
        df_home = pd.DataFrame({
            'Type': ['Wins', 'Draws', 'Losses'],
            'Count': [int(data['home_league_W']), int(data['home_league_D']), int(data['home_league_L'])]
        })
        st.bar_chart(df_home.set_index('Type'))

    # Away Stats
    with col8:
        st.subheader('Away Stats')
        df_away = pd.DataFrame({
            'Type': ['Wins', 'Draws', 'Losses'],
            'Count': [int(data['away_league_W']), int(data['away_league_D']), int(data['away_league_L'])]
        })
        st.bar_chart(df_away.set_index('Type'))

    # Display players as captains
    st.subheader('Players as Captains')
    players_as_captain = pd.DataFrame(data['players_as_captain'])
    players_as_captain = players_as_captain.rename(columns={'captain_caps': 'Captain Caps', 'player_name': 'Player Name'})
    st.table(players_as_captain)

    st.header("Players")
    # Display players by position
    for position, players in data['players_by_position'].items():
        st.markdown("---")  # Add a line divider
        st.header(position)
        for i in range(0, len(players), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(players):
                    player = players[i + j]
                    with cols[j]:
                        # Check if the image URL is valid
                        responsepic = requests.get(player['player_image'])
                        if responsepic.status_code == 200:
                            st.image(player['player_image'])
                        else:
                            st.image('default.png',width=150)  # Display a default image if the URL is not valid
                        st.subheader(player['player_name'])
                        st.write(':shirt: Number:', player['player_number'])
                        st.write(':runner: Matches Played:', player['player_match_played'])
                        st.write(':star: Rating:', player['player_rating'])
    st.markdown("---")
    # Check if key_player data exists in the response
    if 'key_player' in data:
        # Create a new section for key players
        st.header('Key Players')

        # Create a mapping for the keys to the desired display text
        key_mapping = {
            'player_goals_conceded': 'Goal',
            'player_saves': 'Saves',
            'player_passes_accuracy': 'Pass Acc',
            'player_match_played': 'Played'
        }

        # Create columns for key players
        cols = st.columns(len(data['key_player']))

        # Loop through the key player data and display each player's information in a column
        for i, player in enumerate(data['key_player']):
            # Check if the image URL is valid
            responsepic = requests.get(player['player_image'])
            if responsepic.status_code == 200:
                cols[i].image(player['player_image'])
            else:
                cols[i].image('default.png', width=150)  # Display a default image if the URL is not valid

            # Create a placeholder for the player's name with a maximum height
            name_placeholder = cols[i].empty()
            name_placeholder.markdown(f"<div style='max-height: 50px;'>{player['player_name']}</div>", unsafe_allow_html=True)
            for key, value in player.items():
                if key not in ['player_name', 'player_image']:
                    # Use the key_mapping to get the display text for the key
                    display_text = key_mapping.get(key, key)
                    cols[i].text(f"{display_text}: {value}")
    # Recent Match
    st.markdown("---")
    response1 = requests.get(f'http://localhost:5000/recent_match?team_name={selected_team}')
    data1 = response1.json()

    # Create a new section
    st.header('Recent Matches')

    # Create a carousel
    cols = st.columns(len(data1['matches']))

    for i, match in enumerate(data1['matches']):
        with cols[i]:
            st.markdown(f"<h5 style='text-align: center; color: white;'>{match['match_hometeam_name']} vs {match['match_awayteam_name']}</h3>", unsafe_allow_html=True)
            st.empty()
            st.image([match['team_home_badge'], match['team_away_badge']], width=100)
            st.empty()
            st.write(f":soccer: Final Score: {match['match_hometeam_ft_score']} - {match['match_awayteam_ft_score']}")
            st.empty()
            st.write(f":spiral_calendar_pad: {match['match_date']}")

    st.markdown("---")
    # Goal Difference Stats
    st.header('Goal Difference Stats')
    # Fetch the data from the API
    responsegd = requests.get(f'http://localhost:5000/goal-differencesv2?team={selected_team}')
    data = responsegd.json()
    #Forecast
    url = "http://localhost:5000/predict"
    forecast = data["goal_difference"]
    responsefor = requests.post(url, data=json.dumps(forecast), headers={'Content-Type': 'application/json'})
    new_data = responsefor.json()

    # Convert the goal_difference data to a DataFrame and sort it by date
    df1 = pd.DataFrame(data['goal_difference'])
    df1['date'] = pd.to_datetime(df1['date'])
    df1.sort_values('date', inplace=True)

    # Get the last date in the sorted goal_difference data
    last_date = df1.iloc[-1]['date']

    new_goal_difference = []
    # Add a week to the last_date before starting the loop
    last_date += pd.DateOffset(weeks=1)
    for i, (date, goal_difference) in enumerate(new_data.items()):
        new_date = (last_date + pd.DateOffset(weeks=i)).isoformat()
        new_goal_difference.append({'date': new_date, 'goal_difference': goal_difference})

    data['goal_difference'].extend(new_goal_difference)

    # Convert the data to a DataFrame
    df = pd.DataFrame(data['goal_difference'])
    # Convert the 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'])
    # Set the 'date' column as the index
    df.set_index('date', inplace=True)
    # Sort the DataFrame by the date
    df.sort_index(inplace=True)
    # Create a line chart with markers
    fig = go.Figure()
    # Add the first part of the data
    fig.add_trace(go.Scatter(x=df.index[:-3], y=df['goal_difference'][:-3], mode='lines+markers', name='Actual Goal Difference'))
    # Add the last three entries
    fig.add_trace(go.Scatter(x=df.index[-3:], y=df['goal_difference'][-3:], mode='lines+markers', name='Pedicted Goal Difference', line=dict(color='red')))
    # Display the line chart in Streamlit
    st.plotly_chart(fig)

    st.markdown("---")
    # Team Stats
    st.header('Team Stats')
    # Get data from API
    responsestat = requests.get(f'http://localhost:5000/team-stat?team={selected_team}')
    data = responsestat.json()

    # Prepare data for radar chart
    labels = list(data.keys())
    stats = list(data.values())
    # Create radar chart
    fig = go.Figure(data=go.Scatterpolar(
        r=stats,
        theta=labels,
        fill='toself',
    ))
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True
            )),
        showlegend=False
    )
    # Show the plot in Streamlit
    st.plotly_chart(fig)

def player_analysis():
    st.header("Player Analysis")
    # Add your code for the Player Analysis page here

# Dictionary mapping page names to functions
pages_dict = {
    "Head to Head": head_to_head,
    "Team Analysis": team_analysis,
    "Player Analysis": player_analysis
}

# Call the function associated with the selected page
pages_dict[selected_page]()