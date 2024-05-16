from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
from datetime import datetime
from dotenv import load_dotenv
import os
from datetime import datetime
import json
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import jsonify
load_dotenv('../.env')

app = Flask(__name__)
es = Elasticsearch("https://localhost:9200", api_key=(os.environ.get("ELASTIC_API_KEY")), verify_certs=False)

def normalize_team_name(team_name):
    if 'Bournemouth' in team_name:
        return 'Bournemouth'
    return team_name

@app.route('/head-to-head', methods=['GET'])
def get_matches():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')

    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "match_date": {
                                "gte": from_date,
                                "lte": to_date,
                                "format": "yyyy-MM-dd"
                            }
                        }
                    },
                    {
                        "bool": {
                            "should": [
                                {"match": {"match_hometeam_name": team1}},
                                {"match": {"match_awayteam_name": team1}},
                                {"match": {"match_hometeam_name": team2}},
                                {"match": {"match_awayteam_name": team2}}
                            ],
                            "minimum_should_match": 2
                        }
                    }
                ]
            }
        }
    }

    res = es.search(index="footballapi.com-events-statistics-v1", body=query)
    scores_list = []
    yellow_cards = {}
    ball_possession = {}
    win_count = {}
    total_goals = {}
    total_shots = {}
    for hit in res['hits']['hits']:
        data = hit['_source']
        data['match_hometeam_name'] = normalize_team_name(data['match_hometeam_name'])
        data['match_awayteam_name'] = normalize_team_name(data['match_awayteam_name'])
        home_team = data['match_hometeam_name']
        away_team = data['match_awayteam_name']
        if home_team not in yellow_cards:
            yellow_cards[home_team] = 0
            ball_possession[home_team] = {'total': 0, 'matches': 0}
            win_count[home_team] = 0
            total_goals[home_team] = 0
            total_shots[home_team] = 0
        if away_team not in yellow_cards:
            yellow_cards[away_team] = 0
            ball_possession[away_team] = {'total': 0, 'matches': 0}
            win_count[away_team] = 0
            total_goals[away_team] = 0
            total_shots[away_team] = 0

        statistics = {stat['type']: {'home': stat['home'], 'away': stat['away']} for stat in data['statistics']}
        winner = 'Draw'
        if data['match_hometeam_ft_score'] > data['match_awayteam_ft_score']:
            winner = data['match_hometeam_name']
        elif data['match_hometeam_ft_score'] < data['match_awayteam_ft_score']:
            winner = data['match_awayteam_name']
        scores = {
            'match_date': data['match_date'],
            'match_hometeam_name': data['match_hometeam_name'],
            'match_awayteam_name': data['match_awayteam_name'],
            'match_hometeam_ft_score': data['match_hometeam_ft_score'],
            'match_awayteam_ft_score': data['match_awayteam_ft_score'],
            'statistics': statistics,
            'winner': winner
        }
        if data['match_hometeam_ft_score'] > data['match_awayteam_ft_score']:
            winner = data['match_hometeam_name']
            win_count[winner] += 1
        elif data['match_hometeam_ft_score'] < data['match_awayteam_ft_score']:
            winner = data['match_awayteam_name']
            win_count[winner] += 1
        scores_list.append(scores)
        for card in data['cards']:
            if card['card'] == 'yellow card':
                if card['home_fault'] != '':
                    yellow_cards[data['match_hometeam_name']] += 1
                if card['away_fault'] != '':
                    yellow_cards[data['match_awayteam_name']] += 1
        if 'Ball Possession' in statistics:
            ball_possession[data['match_hometeam_name']]['total'] += int(statistics['Ball Possession']['home'].rstrip('%'))
            ball_possession[data['match_hometeam_name']]['matches'] += 1
            ball_possession[data['match_awayteam_name']]['total'] += int(statistics['Ball Possession']['away'].rstrip('%'))
            ball_possession[data['match_awayteam_name']]['matches'] += 1
        total_goals[home_team] += int(data['match_hometeam_ft_score'])
        total_goals[away_team] += int(data['match_awayteam_ft_score'])
        if 'Shots Total' in statistics:
            total_shots[home_team] += int(statistics['Shots Total']['home'])
            total_shots[away_team] += int(statistics['Shots Total']['away'])
    avg_ball_possession = {team: possession['total'] / possession['matches'] if possession['matches'] > 0 else 0 for team, possession in ball_possession.items()}
    return {'matches': scores_list, 'summary': {'yellow_cards': yellow_cards, 'avg_ball_possession': avg_ball_possession, 'win_count': win_count, 'total_goals': total_goals, 'total_shots': total_shots}}

@app.route('/goal-differences', methods=['GET'])
def get_goal_differences():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    team = request.args.get('team')
    
    index_name = "footballapi.com-events-statistics-v2"

    query = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                { "term": {"match_team_name": team } },
                {"range": {
                    "match_date": {
                        "lt": from_date,
                        "format": "yyyy-MM-dd"
                    }
                }
                }
                ]
            }
            },

            "aggs": {
                "goal_diff": {
                "sum": {
                    "field": "match_team_goal_difference"
                }
                }
            }
        }
    
    res = es.search(index=index_name, body=query)
    prev_value = res["aggregations"]["goal_diff"]["value"]

    query = {
    "size": 0,
    "query": {
        "bool": {
            "must": [
            { "term": {"match_team_name": team } },
            {"range": {
                            "match_date": {
                                "gte": from_date,
                                "lte": to_date,
                                "format": "yyyy-MM-dd"
                            }
                        }
            }
            ]
        }
        },
    "aggs": {
        "match_day": {
        "terms": { "field": "match_round", "size": 50 },
        "aggs": {
            "goal_diff": {
            "sum": {
                "field": "match_team_goal_difference"
            }
            }
        }
        }
    }
    }
    
    

    res = es.search(index=index_name, body=query)
    
    goal_diff = {}
    goal_diff_cum = {}
    
    for gd in res['aggregations']['match_day']["buckets"]:
        goal_diff[gd["key"]] = gd["goal_diff"]["value"]
        goal_diff_cum[gd["key"]] = gd["goal_diff"]["value"] + prev_value
        prev_value = goal_diff_cum[gd["key"]]
    
    return goal_diff_cum

@app.route('/attacking-stats', methods=['GET'])
def get_attack_stats():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    team = request.args.get('team')
    query = {
    "size": 0,
    "query": {
        "bool": {
            "must": [
            {
                "range": {
                    "match_date": {
                        "gte": from_date,
                        "lte": to_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            },
            { "term": {"match_team_name": team} }
            ]
        }
        },
    "aggs": {
        "match_day": {
        "terms": { "field": "match_round", "size": 50 },
        "aggs": {
            "attacks": {
                "nested" : {
                "path": "player_stats"
                },
                "aggs": {
                    "total_shots": {
                    "sum": {
                        "field": "player_stats.player_total_shots"
                    }  
                },
                "shots_on_goal": {
                    "sum": {
                        "field": "player_stats.player_shots_on_goal"
                    }  
                }
                }
            }
        }
        }
    }
    }
    
    index_name = "footballapi.com-events-statistics-v2"

    res = es.search(index=index_name, body=query)
    
    stats = {}
    for gd in res['aggregations']['match_day']["buckets"]:
        stats[gd["key"]] = dict(
            shot_on_goal=gd["attacks"]["shots_on_goal"]["value"],
            total_shots=gd["attacks"]["total_shots"]["value"],
            effectiveness=gd["attacks"]["shots_on_goal"]["value"]/gd["attacks"]["total_shots"]["value"])

    return stats

@app.route('/player-stats', methods=['GET'])
def get_player_stats():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    player = request.args.get('player')

    query = {
    "size": 50,
    "_source": ["match_round"],
    "query": {
        "bool": {
            "must": [
            {
                "nested": {
                "path":"player_stats",
                "query": {
                    "term": {
                    "player_stats.player_name": player
                    }
                },
                "inner_hits": {}
                }
            },
            {
                "range": {
                    "match_date": {
                        "gte": from_date,
                        "lte": to_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            }
            ]
        }
    }
    }

    index_name = "footballapi.com-events-statistics-v2"

    res = es.search(index=index_name, query=query["query"], size=query["size"], source=query["_source"])
    
    stats = {}
    for h in res['hits']['hits']:
        stats[int(h["_source"]["match_round"])] = h["inner_hits"]["player_stats"]["hits"]["hits"][0]["_source"]

    return stats

@app.route('/team', methods=['GET'])
def get_team():
    team_name = request.args.get('team_name')
    if not team_name:
        return {"error": "Missing team_name parameter"}, 400

    query = {
        "_source": ["team_name", "team_founded", "team_badge", "venue.venue_name", "players", "coaches", "overall_league_position", "overall_league_W", "overall_league_D", "overall_league_L", "home_league_W", "home_league_D", "home_league_L", "away_league_W", "away_league_D", "away_league_L"],
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"team_name": team_name}}
                ]
            }
        }
    }
    res = es.search(index="search-teams_stat_v1", body=query)
    if res['hits']['hits']:
        source = res['hits']['hits'][0]['_source']
        # Filter players where player_is_captain is more than '0' and only return player_name and player_is_captain
        players_as_captain = [{"player_name": player['player_name'], "captain_caps": player['player_is_captain']} for player in source['players'] if player.get('player_is_captain', '0').isdigit() and int(player.get('player_is_captain', '0')) > 0]
        # Get coach_name as a string
        coach_name = source['coaches'][0]['coach_name'] if source['coaches'] else None

        # Group players by their positions
        positions = ['Goalkeepers', 'Defenders', 'Midfielders', 'Forwards']
        players_by_position = {position: [] for position in positions}
        for player in source['players']:
            if player['player_type'] in positions:
                players_by_position[player['player_type']].append({
                    'player_name': player['player_name'],
                    'player_match_played': player['player_match_played'],
                    'player_number': player['player_number'],
                    'player_image': player['player_image'],
                    'player_rating': player['player_rating']
                })
        # Initialize key_player array
        key_player = []

        # Define the attributes to check
        attributes = ['player_goals', 'player_saves', 'player_passes_accuracy', 'player_match_played']

        # For each attribute, find the player with the highest value
        for attribute in attributes:
            max_value = 0
            max_player = None
            for player in source['players']:
                # Check if the attribute is a digit
                if player.get(attribute, '0').isdigit():
                    # If the player's attribute value is greater than the current max_value, update max_value and max_player
                    if int(player.get(attribute, '0')) > max_value:
                        max_value = int(player.get(attribute, '0'))
                        max_player = player
            # Add the player with the highest attribute value to the key_player array
            if max_player is not None:
                key_player.append({
                    'player_name': max_player['player_name'],
                    'player_image': max_player['player_image'],
                    attribute: max_player[attribute]
                })

        return {
            "team_name": source['team_name'],
            "team_founded": source['team_founded'],
            "team_badge": source['team_badge'],
            "venue_name": source['venue']['venue_name'],
            "players_as_captain": players_as_captain,
            "number_of_captains": len(players_as_captain),
            "coach_name": coach_name,
            "players_by_position": players_by_position,
            "key_player": key_player,
            "overall_league_position": source['overall_league_position'],
            "overall_league_W": source['overall_league_W'],
            "overall_league_D": source['overall_league_D'],
            "overall_league_L": source['overall_league_L'],
            "home_league_W": source['home_league_W'],
            "home_league_D": source['home_league_D'],
            "home_league_L": source['home_league_L'],
            "away_league_W": source['away_league_W'],
            "away_league_D": source['away_league_D'],
            "away_league_L": source['away_league_L']
        }
    else:
        return {"error": "No team found with the provided team_name"}, 404
@app.route('/recent_match', methods=['GET'])
def recent_match():
    team_name = request.args.get('team_name')
    query = {
        "size": 4,
        "sort": [
            {
                "match_date": {
                    "order": "desc"
                }
            }
        ],
        "query": {
            "bool": {
                "should": [
                    {"match_phrase": {"match_hometeam_name": team_name}},
                    {"match_phrase": {"match_awayteam_name": team_name}}
                ],
                "minimum_should_match": 1
            }
        }
    }

    res = es.search(index="search-apifootball", body=query)
    matches = [hit['_source'] for hit in res['hits']['hits']]

    # Check if all attributes exist in the data
    required_attributes = ['match_hometeam_name', 'match_awayteam_name', 'match_date']
    for match in matches:
        if not all(attr in match for attr in required_attributes):
            return {'error': 'One or more matches do not have all the required attributes.'}, 400

    # Only return the specified fields
    fields_to_return = ['match_hometeam_name', 'match_awayteam_name', 'match_awayteam_ft_score', 'match_hometeam_ft_score', 'team_away_badge', 'team_home_badge', 'match_hometeam_id', 'match_awayteam_id', 'match_date']
    matches = [{field: match[field] for field in fields_to_return if field in match} for match in matches]

    return {'matches': matches}
@app.route('/goal-differencesv2', methods=['GET'])
def goal_differencesv2():
    team = request.args.get('team')
    index_name = "search-footballapi.com-events-statistics-v3"

    query = {
        "size": 10000,
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"match_team_name": team}},
                    {"match_phrase": {"league_year": "2023/2024"}}
                ]
            }
        }
    }   

    res = es.search(index=index_name, body=query)

    # Extract the '_source' field from each hit
    data = [hit['_source'] for hit in res['hits']['hits']]

    # Initialize the goal difference array
    goal_difference = []

    # Calculate the cumulative goal difference
    # Calculate the cumulative goal difference
    for match in data:
        goal_diff = match['match_team_goal_difference']
        match_date = match['match_date']  # assuming 'match_date' is the correct field name
        if goal_difference:
            cumulative_goal_diff = goal_difference[-1]["goal_difference"] + goal_diff
            goal_difference.append({"date": match_date, "goal_difference": cumulative_goal_diff})
        else:
            goal_difference.append({"date": match_date, "goal_difference": goal_diff})
    print(len(goal_difference))
    return {"goal_difference": goal_difference}
@app.route('/team-stat', methods=['GET'])
def team_stat():
    team = request.args.get('team')
    index_name = "search-footballapi.com-events-statistics-v3"

    query = {
        "size": 10000,
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"match_team_name": team}},
                    {"match_phrase": {"league_year": "2023/2024"}}
                ]
            }
        }
    }   

    res = es.search(index=index_name, body=query)

    # Extract the '_source' field from each hit
    data = [hit['_source'] for hit in res['hits']['hits']]

    # Extract the required fields from 'statistics' and convert to int if they are digits
    shots_total = [int(d['statistics']['shots_total']) if str(d['statistics']['shots_total']).isdigit() else d['statistics']['shots_total'] for d in data]
    ball_possession = [int(d['statistics']['ball_possession']) if str(d['statistics']['ball_possession']).isdigit() else d['statistics']['ball_possession'] for d in data]
    saves = [int(d['statistics']['saves']) if str(d['statistics']['saves']).isdigit() else d['statistics']['saves'] for d in data]
    passes_total = [int(d['statistics']['passes_total']) if str(d['statistics']['passes_total']).isdigit() else d['statistics']['passes_total'] for d in data]
    corners = [int(d['statistics']['corners']) if str(d['statistics']['corners']).isdigit() else d['statistics']['corners'] for d in data]

    # Calculate the mean of the extracted fields
    mean_shots_total = np.mean(shots_total)
    mean_ball_possession = np.mean(ball_possession)
    mean_saves = np.mean(saves)
    mean_passes_total = np.mean(passes_total)
    mean_corners = np.mean(corners)

    return {
        'mean_shots_total': mean_shots_total,
        'mean_ball_possession': mean_ball_possession,
        'mean_saves': mean_saves,
        'mean_passes_total': mean_passes_total,
        'mean_corners': mean_corners
    }
@app.route('/predict', methods=['POST'])
def predict():
    # Get the data from the request
    goal_difference_data = request.get_json()

    # Convert data to DataFrame
    df = pd.DataFrame(goal_difference_data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    # Fit ARIMA model
    model = ARIMA(df['goal_difference'], order=(1, 1, 1))
    model_fit = model.fit()

    # Forecast next value
    forecast = model_fit.forecast(steps=3)
    # Return forecasted value
    return(forecast.to_dict())
@app.route('/all_teams', methods=['GET'])
def all_teams():
    res = es.search(index="search-teams_stat_v1", body={"size": 10000,"query": {"match_all": {}}})
    team_names = [doc['_source']['team_name'] for doc in res['hits']['hits']]
    return jsonify(team_names)
@app.route('/')
def home():
    return render_template('index.html')
    
if __name__ == '__main__':
    app.run(debug=True)