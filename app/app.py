from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
from datetime import datetime
from dotenv import load_dotenv
import os

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

@app.route('/')
def home():
    return render_template('index.html')
    
if __name__ == '__main__':
    app.run(debug=True)