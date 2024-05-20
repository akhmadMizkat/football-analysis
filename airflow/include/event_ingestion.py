import requests
from elasticsearch import Elasticsearch
import os
from include.football_parser_v2 import parse_lineup, parse_player_stats, parse_statistics
from include.utils import APIError

def match_document_builder(index, raw_match, position):
    def key_friendly_str(key):
        return key.replace(' ', '_').lower()

    match_metadata = {
            "index": {
                "_index": index,
                "_id": f'{raw_match["match_id"]}_{position}'
            }
        }
    
    reverse_position = "home" if position == "away" else "away"
    
    match = dict(
        match_id=raw_match["match_id"],
        team_position=position,
        country_id=raw_match["country_id"],
        country_name=raw_match["country_name"],
        league_id=raw_match["league_id"],
        league_name=raw_match["league_name"],
        match_date=raw_match["match_date"],
        match_status=raw_match["match_status"],
        match_time=raw_match["match_time"],
        match_team_id=raw_match[f"match_{position}team_id"],
        match_team_name=raw_match[f"match_{position}team_name"],
        match_team_score=raw_match[f"match_{position}team_score"],
        match_team_halftime_score=raw_match[f"match_{position}team_halftime_score"],
        match_team_extra_score=raw_match[f"match_{position}team_extra_score"],
        match_team_penalty_score=raw_match[f"match_{position}team_penalty_score"],
        match_team_ft_score=raw_match[f"match_{position}team_ft_score"],
        match_team_conceded=raw_match[f"match_{reverse_position}team_score"],
        match_team_halftime_conceded=raw_match[f"match_{reverse_position}team_halftime_score"],
        match_team_extra_conceded=raw_match[f"match_{reverse_position}team_extra_score"],
        match_team_penalty_conceded=raw_match[f"match_{reverse_position}team_penalty_score"],
        match_team_ft_conceded=raw_match[f"match_{reverse_position}team_ft_score"],
        match_team_goal_difference=int(raw_match[f"match_{position}team_ft_score"])-int(raw_match[f"match_{reverse_position}team_ft_score"]),
        match_team_system=raw_match[f"match_{position}team_system"],
        match_live=raw_match["match_live"],
        match_round=raw_match["match_round"],
        match_stadium=raw_match["match_stadium"],
        match_referee=raw_match["match_referee"],
        team_badge=raw_match[f"team_{position}_badge"],
        league_logo=raw_match["league_logo"],
        country_logo=raw_match["country_logo"],
        league_year=raw_match["league_year"],
        fk_stage_key=raw_match["fk_stage_key"],
        stage_name=raw_match["stage_name"],
    )

    player_stats = []
    for p in raw_match["player_stats"][position]:
        p["team_position"] = position
        p["player_team_id"] = match["match_team_id"]
        p["player_team_name"] = match["match_team_name"]
        player_stats.append(parse_player_stats(p))

    match["player_stats"] = player_stats

    lineup = []
    for status in raw_match["lineup"][position]:
        for p in raw_match["lineup"][position][status]:
            p["team_position"] = position
            p["player_team_id"] = match["match_team_id"]
            p["player_team_name"] = match["match_team_name"]
            p["status"] = status
            lineup.append(p)
    
    match["lineup"] = lineup

    game_stats = {key_friendly_str(s["type"]): s[position] for s in raw_match["statistics"]}
    game_stats["team_position"] = position
    game_stats["team_id"] = match["match_team_id"]
    game_stats["team_name"] = match["match_team_name"]
    match["statistics"] = parse_statistics(game_stats)

    goalscorer = []
    for p in raw_match["goalscorer"]:
        if p[f"{position}_scorer_id"] != "":
            scorer = {}
            scorer["team_position"] = position
            scorer["team_id"] = match[f"match_team_id"]
            scorer["team_name"] = match[f"match_team_name"]            
            scorer["time"] = p["time"],
            scorer["player_name"]=p[f"{position}_scorer"]
            scorer["player_id"]=p[f"{position}_scorer_id"]
            scorer["player_assist_name"]=p[f"{position}_assist"]
            scorer["player_assist_id"]=p[f"{position}_assist_id"]
            scorer["score"]=p["score"]
            scorer["info"]=p["info"]
            scorer["score_info_time"]=p["score_info_time"]

            goalscorer.append(scorer) 
    match["goalscorer"] = goalscorer

    cards = []
    for p in raw_match["cards"]:
        if p[f"{position}_fault"] != "":
            fault = {}
            fault["team_position"] = position
            fault["team_id"] = match[f"match_team_id"]
            fault["team_name"] = match[f"match_team_name"]            
            fault["time"] = p["time"],
            fault["player_name"]=p[f"{position}_fault"]
            fault["player_id"]=p[f"{position}_player_id"]
            fault["card"]=p["card"]
            fault["info"]=p["info"]
            fault["score_info_time"]=p["score_info_time"]

            cards.append(fault) 
    match["cards"] = cards

    return (match_metadata, match)


def ingest_events(league_id, start, end):
    api_key = os.environ.get("FOOTBALL_API_KEY")
    # start="2023-08-07"
    # end="2023-08-14"
    url = f"https://apiv3.apifootball.com/?action=get_events&from={start}&to={end}&league_id={league_id}&match_live=0&withPlayerStats=1&timezone=Asia/Jakarta&APIkey={api_key}"
    print(url)
    # Connect to Elasticsearch with SSL certificate verification disabled
    client = Elasticsearch("https://host.docker.internal:9200", api_key=(os.environ.get("ELASTIC_API_KEY")), verify_certs=False)
    index_name = "footballapi.com-events-statistics-v2"

    response = requests.get(url, timeout=60)

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and "error" in data:
            m=data["message"]
            raise APIError(f"Error response from API with message {m}")
        
        documents = []
        for raw_match in data:
            for position in ["home", "away"]:
                match_metadata, match = match_document_builder(index_name, raw_match, position)
                documents.append(match_metadata)
                documents.append(match)
        try:
            print(client.bulk(operations=documents, pipeline="ent-search-generic-ingestion"))
            print("Ingested data into Elasticsearch")
        except Exception as e:
            print("Failed to ingest data:", e)
            raise e
    else:
        raise APIError(f"Request failed with status code {response.status_code}")