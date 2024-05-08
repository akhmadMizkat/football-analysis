import requests
import json
from elasticsearch import Elasticsearch

from dotenv import load_dotenv
import os

load_dotenv()

url = f"https://apiv3.apifootball.com/?action=get_events&from=2018-03-01&to=2023-08-12&league_id=152&match_live=0&timezone=Asia/Jakarta&APIkey={os.environ.get("FOOTBALL_API_KEY")}"

# Connect to Elasticsearch with SSL certificate verification disabled
client = Elasticsearch("https://localhost:9200", api_key=(os.environ.get("ELASTIC_API_KEY")), verify_certs=False)

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("Received data:", data)
    documents = []
    for item in data:
        index_metadata = {
            "index": {
                "_index": "footballapi.com-events-statistics-v1",
                "_id": item["match_id"]
            }
        }
        documents.append(index_metadata)
        documents.append(item)

    try:
        client.bulk(operations=documents, pipeline="ent-search-generic-ingestion")
        print("Ingested data into Elasticsearch")
    except Exception as e:
        print("Failed to ingest data:", e)
else:
    print(f"Request failed with status code {response.status_code}")