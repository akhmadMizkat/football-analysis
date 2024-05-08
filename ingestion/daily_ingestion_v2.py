import requests
import json
from elasticsearch import Elasticsearch
from ingester import match_document_builder
import os
from dotenv import load_dotenv

from football_parser_v2 import parse_player_stats, parse_statistics

def load_json_from_file(file_path):
    """
    Load JSON data from a file and return it as a dictionary.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The JSON data loaded as a dictionary.
    """
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    return json_data

load_dotenv("../.env")

url = f"https://apiv3.apifootball.com/?action=get_events&from=2018-03-01&to=2023-08-12&league_id=152&match_live=0&withPlayerStats=1&timezone=Asia/Jakarta&APIkey={os.environ.get("FOOTBALL_API_KEY")}"

# Connect to Elasticsearch with SSL certificate verification disabled
client = Elasticsearch("https://localhost:9200", api_key=(os.environ.get("ELASTIC_API_KEY")), verify_certs=False)
index_name = "footballapi.com-events-statistics-v2"

response = requests.get(url, timeout=60)

if response.status_code == 200:
    data = response.json()
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
else:
    print(f"Request failed with status code {response.status_code}")