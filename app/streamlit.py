import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from sklearn.preprocessing import Normalizer
import json
import plotly.express as px
import unidecode
from typing import List
from streamlit_searchbox import st_searchbox
# from fbprophet import Prophet
# Set page configuration
# Define the pages

def remove_accents(text: str) -> str:
    return unidecode.unidecode(text)

st.set_page_config(layout="centered")
gk_list = pd.DataFrame(requests.get("http://localhost:5000/search-players?type=Goalkeepers").json())
def_list = pd.DataFrame(requests.get("http://localhost:5000/search-players?type=Defenders").json())
mid_list = pd.DataFrame(requests.get("http://localhost:5000/search-players?type=Midfielders").json())
fw_list = pd.DataFrame(requests.get("http://localhost:5000/search-players?type=Forwards").json())



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
    tab1, tab2, tab3, tab4 = st.tabs(["Goalkeepers", "Defenders", "Midfielders", "Forwards"])
    
    with tab1:
        st.subheader('Top 3 GKs')
        # Fetch the team names from the API
        gk_stats = requests.get('http://localhost:5000/gk-stats').json()
        df_gk = pd.DataFrame(gk_stats)
        df_gk["player_saves"] =  pd.to_numeric(df_gk["player_saves"])
        df_gk["player_match_played"] =  pd.to_numeric(df_gk["player_match_played"])
        df_gk["player_goals_conceded"] =  pd.to_numeric(df_gk["player_goals_conceded"])
        df_gk["match_conceded_ratio"] = df_gk["player_match_played"]/df_gk["player_goals_conceded"]
        
        top_3_gk = df_gk.sort_values(by='match_conceded_ratio', ascending=False).head(3)
        
        top_gk_cols = st.columns(3)
        
        for i in range(3):
            with top_gk_cols[i]:
                player = top_3_gk.iloc[i]
                responsepic = requests.get(player['player_image'])
                if responsepic.status_code == 200:
                    st.image(player['player_image'])
                else:
                    st.image('default.png',width=150)
                st.subheader(player['player_name'])
                st.write(':shirt: Team:', player['team_name'])
                st.write(':runner: Matches Played:', player['player_match_played'])
                st.write(':star: Match & Goal Ratio:', round(player['match_conceded_ratio'], 2))
    
        fig = px.scatter(
            df_gk,
            x="player_match_played",
            y="player_goals_conceded",
            # size="player_saves",
            color="player_saves",
            hover_name="player_name",
            log_x=True,
            size_max=60,
        )
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        selected_gks = []
        st.markdown("---")  # Add a line divider
        st.subheader("Player Comparison")
        with st.expander("Select Goalkeeper 1", expanded=True):               
            selected_gk1 = st.selectbox('Select a player', [""]+gk_list["player_name"].to_list(), key="gk1")
            col1, col2  = st.columns([1,3])

            if selected_gk1 != "":
                gk1 = df_gk[df_gk["player_name"] == selected_gk1].iloc[0]
                selected_gks.append(gk1)
                with col1:
                    st.subheader(selected_gk1)
                    responsepic = requests.get(gk1['player_image'])
                    if responsepic.status_code == 200:
                        st.image(gk1['player_image'])
                    else:
                        st.image('default.png',width=150)
                    st.subheader(gk1["team_name"])

                with col2:
                    st.caption("📄 Information of Player")
                    col_1, col_2, col_3, col_4 = st.columns(4)

                    with col_1:
                        st.metric("Age", gk1["player_age"], None)
                        st.metric("Rating", gk1["player_rating"], None)

                    with col_2:
                        st.metric("Match Played", gk1["player_match_played"], None)
                        st.metric("GC", gk1["player_goals_conceded"], help="Goal Conceded")

                    with col_3:
                        st.metric("Saves", gk1["player_saves"], None)
                        st.metric("IBS", gk1["player_inside_box_saves"], help="Inside Box Saves")
                    
                    with col_4:
                        st.metric("Clerances", gk1["player_clearances"], None)
                        st.metric("Dules Won", gk1["player_duels_won"], None)
        
        with st.expander("Select Goalkeeper 2", expanded=True):               
            selected_gk2 = st.selectbox('Select a player', [""]+gk_list["player_name"].to_list(), key="gk2")
            col1, col2  = st.columns([1,3])

            if selected_gk2 != "":
                gk2 = df_gk[df_gk["player_name"] == selected_gk2].iloc[0]
                selected_gks.append(gk2)
                with col1:
                    st.subheader(selected_gk2)
                    responsepic = requests.get(gk2['player_image'])
                    if responsepic.status_code == 200:
                        st.image(gk2['player_image'])
                    else:
                        st.image('default.png',width=150)
                    st.subheader(gk2["team_name"])

                with col2:
                    st.caption("📄 Information of Player")
                    col_1, col_2, col_3, col_4 = st.columns(4)

                    with col_1:
                        st.metric("Age", gk2["player_age"], None)
                        st.metric("Rating", gk2["player_rating"], None)

                    with col_2:
                        st.metric("Match Played", gk2["player_match_played"], None)
                        st.metric("GC", gk2["player_goals_conceded"], help="Goal Conceded")

                    with col_3:
                        st.metric("Saves", gk2["player_saves"], None)
                        st.metric("IBS", gk2["player_inside_box_saves"], help="Inside Box Saves")
                    
                    with col_4:
                        st.metric("Clerances", gk2["player_clearances"], None)
                        st.metric("Dules Won", gk2["player_duels_won"], None)
        
        ###### Radar Analytics #########################
        categories = ['player_match_played', 'player_goals_conceded', 'player_saves', 'player_inside_box_saves', 'player_clearances', 'player_duels_won']
        selected_players = selected_gks

        fig = go.Figure()
        colors=["blue", "orange"]
        i = 0
        for player_row in selected_players:
            player_name = player_row['player_name']
            values = [player_row[col] for col in categories]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=player_name,
                marker = dict(color = colors[i]),
            ))

            i += 1

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                )
            ),
            showlegend=True,  
            legend=dict(
                orientation="v", 
                yanchor="top",  
                y=1,  
                xanchor="left",  
                x=1.02,  
            ),
            width=750,  
            height=520  
        )

        st.plotly_chart(fig, use_container_width=True)
                    
    with tab2:
        st.subheader('Top 3 Defenders')
        def_stats = requests.get('http://localhost:5000/defender-stats').json()
        df_gk = pd.DataFrame(def_stats)
        df_gk["player_match_played"] =  pd.to_numeric(df_gk["player_match_played"])
        df_gk["player_fouls_committed"] =  pd.to_numeric(df_gk["player_fouls_committed"])
        df_gk["player_clearances"] =  pd.to_numeric(df_gk["player_clearances"])
        df_gk["cpm"] = df_gk["player_clearances"]/df_gk["player_match_played"]
        
        top_3_gk = df_gk.sort_values(by='cpm', ascending=False).head(3)
        
        top_gk_cols = st.columns(3)
        
        for i in range(3):
            with top_gk_cols[i]:
                player = top_3_gk.iloc[i]
                responsepic = requests.get(player['player_image'])
                if responsepic.status_code == 200:
                    st.image(player['player_image'])
                else:
                    st.image('default.png',width=150)
                st.subheader(player['player_name'])
                st.write(':shirt: Team:', player['team_name'])
                st.write(':runner: Matches Played:', player['player_match_played'])
                st.write(':star: Clearence per Match:', round(player['cpm'], 2))
    
        fig = px.scatter(
            df_gk,
            x="player_match_played",
            y="player_clearances",
            # size="player_saves",
            color="player_fouls_committed",
            hover_name="player_name",
            log_x=True,
            size_max=60,
        )
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        selected_gks = []
        st.markdown("---")  # Add a line divider
        st.subheader("Player Comparison")
        with st.expander("Select Defender 1", expanded=True):               
            selected_gk1 = st.selectbox('Select a player', [""]+def_list["player_name"].to_list(), key="def1")
            col1, col2  = st.columns([1,3])

            if selected_gk1 != "":
                gk1 = df_gk[df_gk["player_name"] == selected_gk1].iloc[0]
                selected_gks.append(gk1)
                with col1:
                    st.subheader(selected_gk1)
                    responsepic = requests.get(gk1['player_image'])
                    if responsepic.status_code == 200:
                        st.image(gk1['player_image'])
                    else:
                        st.image('default.png',width=150)
                    st.subheader(gk1["team_name"])

                with col2:
                    st.caption("📄 Information of Player")
                    col_1, col_2, col_3, col_4 = st.columns(4)

                    with col_1:
                        st.metric("Age", gk1["player_age"], None)
                        st.metric("Rating", gk1["player_rating"], None)

                    with col_2:
                        st.metric("Match Played", gk1["player_match_played"], None)
                        st.metric("Clearance", gk1["player_clearances"])

                    with col_3:
                        st.metric("Red Card", gk1["player_red_cards"], None)
                        st.metric("Yellow Card", gk1["player_yellow_cards"])
                    
                    with col_4:
                        st.metric("Duels Total", gk1["player_duels_total"], None)
                        st.metric("Duels Won", gk1["player_duels_won"], None)
        
        with st.expander("Select Defender 2", expanded=True):               
            selected_gk1 = st.selectbox('Select a player', [""]+def_list["player_name"].to_list(), key="def2")
            col1, col2  = st.columns([1,3])

            if selected_gk1 != "":
                gk1 = df_gk[df_gk["player_name"] == selected_gk1].iloc[0]
                selected_gks.append(gk1)
                with col1:
                    st.subheader(selected_gk1)
                    responsepic = requests.get(gk1['player_image'])
                    if responsepic.status_code == 200:
                        st.image(gk1['player_image'])
                    else:
                        st.image('default.png',width=150)
                    st.subheader(gk1["team_name"])

                with col2:
                    st.caption("📄 Information of Player")
                    col_1, col_2, col_3, col_4 = st.columns(4)

                    with col_1:
                        st.metric("Age", gk1["player_age"], None)
                        st.metric("Rating", gk1["player_rating"], None)

                    with col_2:
                        st.metric("Match Played", gk1["player_match_played"], None)
                        st.metric("Clearance", gk1["player_clearances"])

                    with col_3:
                        st.metric("Red Card", gk1["player_red_cards"], None)
                        st.metric("Yellow Card", gk1["player_yellow_cards"])
                    
                    with col_4:
                        st.metric("Duels Total", gk1["player_duels_total"], None)
                        st.metric("Duels Won", gk1["player_duels_won"], None)
        
        ###### Radar Analytics #########################
        categories = ['player_match_played', 'player_clearances', 'player_red_cards', 'player_yellow_cards', 'player_duels_total', 'player_duels_won',
                      'player_blocks', 'player_fouls_committed', 'player_interceptions', 'player_tackles']
        selected_players = selected_gks

        fig = go.Figure()
        colors=["blue", "orange"]
        i = 0
        for player_row in selected_players:
            player_name = player_row['player_name']
            values = [player_row[col] for col in categories]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=player_name,
                marker = dict(color = colors[i]),
            ))

            i += 1

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                )
            ),
            showlegend=True,  
            legend=dict(
                orientation="v", 
                yanchor="top",  
                y=1,  
                xanchor="left",  
                x=1.02,  
            ),
            width=750,  
            height=520  
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader('Top 3 Midfielders')
        mid_stats = requests.get('http://localhost:5000/midfielders-stats').json()
        df_players = pd.DataFrame(mid_stats)
        df_players["player_match_played"] =  pd.to_numeric(df_players["player_match_played"])
        df_players["player_key_passes"] =  pd.to_numeric(df_players["player_key_passes"])
        df_players["player_passes"] =  pd.to_numeric(df_players["player_passes"])
        df_players["kppm"] = df_players["player_key_passes"]/df_players["player_match_played"]
        
        top_3_gk = df_players.sort_values(by='kppm', ascending=False).head(3)
        
        top_gk_cols = st.columns(3)
        
        for i in range(3):
            with top_gk_cols[i]:
                player = top_3_gk.iloc[i]
                responsepic = requests.get(player['player_image'])
                if responsepic.status_code == 200:
                    st.image(player['player_image'])
                else:
                    st.image('default.png',width=150)
                st.subheader(player['player_name'])
                st.write(':shirt: Team:', player['team_name'])
                st.write(':runner: Matches Played:', player['player_match_played'])
                st.write(':star: Key Passes per Match:', round(player['kppm'], 2))
    
        fig = px.scatter(
            df_players,
            x="player_match_played",
            y="player_key_passes",
            # size="player_saves",
            color="player_passes",
            hover_name="player_name",
            log_x=True,
            size_max=60,
        )
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        selected_gks = []
        st.markdown("---")  # Add a line divider
        st.subheader("Player Comparison")
        with st.expander("Select Midfielder 1", expanded=True):               
            selected_gk1 = st.selectbox('Select a player', [""]+mid_list["player_name"].to_list(), key="mid1")
            col1, col2  = st.columns([1,3])

            if selected_gk1 != "":
                gk1 = df_players[df_players["player_name"] == selected_gk1].iloc[0]
                selected_gks.append(gk1)
                with col1:
                    st.subheader(selected_gk1)
                    responsepic = requests.get(gk1['player_image'])
                    if responsepic.status_code == 200:
                        st.image(gk1['player_image'])
                    else:
                        st.image('default.png',width=150)
                    st.subheader(gk1["team_name"])

                with col2:
                    st.caption("📄 Information of Player")
                    col_1, col_2, col_3, col_4 = st.columns(4)

                    with col_1:
                        st.metric("Age", gk1["player_age"], None)
                        st.metric("Rating", gk1["player_rating"], None)

                    with col_2:
                        st.metric("Match Played", gk1["player_match_played"], None)
                        st.metric("Passess Accurracy", gk1["player_passes_accuracy"])

                    with col_3:
                        st.metric("Total Passess", gk1["player_passes"], None)
                        st.metric("Key Passess", gk1["player_key_passes"])
                    
                    with col_4:
                        st.metric("Goals", gk1["player_goals"], None)
                        st.metric("Assist", gk1["player_assists"], None)
        
        with st.expander("Select Midfielder 2", expanded=True):               
            selected_gk1 = st.selectbox('Select a player', [""]+mid_list["player_name"].to_list(), key="mid2")
            col1, col2  = st.columns([1,3])

            if selected_gk1 != "":
                gk1 = df_players[df_players["player_name"] == selected_gk1].iloc[0]
                selected_gks.append(gk1)
                with col1:
                    st.subheader(selected_gk1)
                    responsepic = requests.get(gk1['player_image'])
                    if responsepic.status_code == 200:
                        st.image(gk1['player_image'])
                    else:
                        st.image('default.png',width=150)
                    st.subheader(gk1["team_name"])

                with col2:
                    st.caption("📄 Information of Player")
                    col_1, col_2, col_3, col_4 = st.columns(4)

                    with col_1:
                        st.metric("Age", gk1["player_age"], None)
                        st.metric("Rating", gk1["player_rating"], None)

                    with col_2:
                        st.metric("Match Played", gk1["player_match_played"], None)
                        st.metric("Passess Accurracy", gk1["player_passes_accuracy"])

                    with col_3:
                        st.metric("Total Passess", gk1["player_passes"], None)
                        st.metric("Key Passess", gk1["player_key_passes"])
                    
                    with col_4:
                        st.metric("Goals", gk1["player_goals"], None)
                        st.metric("Assist", gk1["player_assists"], None)
        
        ###### Radar Analytics #########################
        categories = ['player_match_played', 'player_key_passes', 'player_dribble_attempts', 'player_dribble_succ', 'player_duels_total', 'player_duels_won',
                      'player_goals', 'player_assists', 'player_shots_total']
        selected_players = selected_gks

        fig = go.Figure()
        colors=["blue", "orange"]
        i = 0
        for player_row in selected_players:
            player_name = player_row['player_name']
            values = [player_row[col] for col in categories]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=player_name,
                marker = dict(color = colors[i]),
            ))

            i += 1

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                )
            ),
            showlegend=True,  
            legend=dict(
                orientation="v", 
                yanchor="top",  
                y=1,  
                xanchor="left",  
                x=1.02,  
            ),
            width=750,  
            height=520  
        )

        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader('Top 3 Forwards')
        players_stats = requests.get('http://localhost:5000/forwards-stats').json()
        df_players = pd.DataFrame(players_stats)
        df_players["player_match_played"] =  pd.to_numeric(df_players["player_match_played"])
        df_players["player_assists"] =  pd.to_numeric(df_players["player_assists"])
        df_players["player_goals"] =  pd.to_numeric(df_players["player_goals"])
        df_players["gapm"] = (df_players["player_assists"]+df_players["player_goals"])/df_players["player_match_played"]
        
        top_3_players = df_players.sort_values(by='gapm', ascending=False).head(3)
        
        top_pl_cols = st.columns(3)
        
        for i in range(3):
            with top_pl_cols[i]:
                player = top_3_players.iloc[i]
                responsepic = requests.get(player['player_image'])
                if responsepic.status_code == 200:
                    st.image(player['player_image'])
                else:
                    st.image('default.png',width=150)
                st.subheader(player['player_name'])
                st.write(':shirt: Team:', player['team_name'])
                st.write(':runner: Matches Played:', player['player_match_played'])
                st.write(':star: Goal & Assisst per Match:', round(player['gapm'], 2))
    
        fig = px.scatter(
            df_players,
            x="player_match_played",
            y="player_goals",
            # size="player_saves",
            color="gapm",
            hover_name="player_name",
            log_x=True,
            size_max=60,
        )
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        selected_gks = []
        st.markdown("---")  # Add a line divider
        st.subheader("Player Comparison")
        with st.expander("Select Forward 1", expanded=True):               
            selected_gk1 = st.selectbox('Select a player', [""]+fw_list["player_name"].to_list(), key="fw1")
            col1, col2  = st.columns([1,3])

            if selected_gk1 != "":
                gk1 = df_players[df_players["player_name"] == selected_gk1].iloc[0]
                selected_gks.append(gk1)
                with col1:
                    st.subheader(selected_gk1)
                    responsepic = requests.get(gk1['player_image'])
                    if responsepic.status_code == 200:
                        st.image(gk1['player_image'])
                    else:
                        st.image('default.png',width=150)
                    st.subheader(gk1["team_name"])

                with col2:
                    st.caption("📄 Information of Player")
                    col_1, col_2, col_3, col_4 = st.columns(4)

                    with col_1:
                        st.metric("Age", gk1["player_age"], None)
                        st.metric("Rating", gk1["player_rating"], None)

                    with col_2:
                        st.metric("Match Played", gk1["player_match_played"], None)
                        st.metric("Passess Accurracy", gk1["player_passes_accuracy"])

                    with col_3:
                        st.metric("Total Passess", gk1["player_passes"], None)
                        st.metric("Key Passess", gk1["player_key_passes"])
                    
                    with col_4:
                        st.metric("Goals", gk1["player_goals"], None)
                        st.metric("Assist", gk1["player_assists"], None)
        
        with st.expander("Select Forward 2", expanded=True):               
            selected_gk1 = st.selectbox('Select a player', [""]+fw_list["player_name"].to_list(), key="fw2")
            col1, col2  = st.columns([1,3])

            if selected_gk1 != "":
                gk1 = df_players[df_players["player_name"] == selected_gk1].iloc[0]
                selected_gks.append(gk1)
                with col1:
                    st.subheader(selected_gk1)
                    responsepic = requests.get(gk1['player_image'])
                    if responsepic.status_code == 200:
                        st.image(gk1['player_image'])
                    else:
                        st.image('default.png',width=150)
                    st.subheader(gk1["team_name"])

                with col2:
                    st.caption("📄 Information of Player")
                    col_1, col_2, col_3, col_4 = st.columns(4)

                    with col_1:
                        st.metric("Age", gk1["player_age"], None)
                        st.metric("Rating", gk1["player_rating"], None)

                    with col_2:
                        st.metric("Match Played", gk1["player_match_played"], None)
                        st.metric("Passess Accurracy", gk1["player_passes_accuracy"])

                    with col_3:
                        st.metric("Total Passess", gk1["player_passes"], None)
                        st.metric("Key Passess", gk1["player_key_passes"])
                    
                    with col_4:
                        st.metric("Goals", gk1["player_goals"], None)
                        st.metric("Assist", gk1["player_assists"], None)
        
        ###### Radar Analytics #########################
        categories = ['player_match_played', 'player_key_passes', 'player_dribble_attempts', 'player_dribble_succ', 'player_duels_total', 'player_duels_won',
                      'player_goals', 'player_assists', 'player_shots_total']
        selected_players = selected_gks

        fig = go.Figure()
        colors=["blue", "orange"]
        i = 0
        for player_row in selected_players:
            player_name = player_row['player_name']
            values = [player_row[col] for col in categories]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=player_name,
                marker = dict(color = colors[i]),
            ))

            i += 1

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                )
            ),
            showlegend=True,  
            legend=dict(
                orientation="v", 
                yanchor="top",  
                y=1,  
                xanchor="left",  
                x=1.02,  
            ),
            width=750,  
            height=520  
        )

        st.plotly_chart(fig, use_container_width=True)
    # # Display team name in the second column
    # with col2:
    #     st.title("Test")

    # Create columns for founded, venue, coach, and position
    # col3, col4, col5, col6 = st.columns(4)


# Dictionary mapping page names to functions
pages_dict = {
    "Head to Head": head_to_head,
    "Team Analysis": team_analysis,
    "Player Analysis": player_analysis
}

# Call the function associated with the selected page
pages_dict[selected_page]()