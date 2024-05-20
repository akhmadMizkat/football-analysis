import requests
from elasticsearch import Elasticsearch
import os
import dotenv

dotenv.load_dotenv("../.env")

url = "https://apiv3.apifootball.com/?action=get_teams&league_id=152&APIkey=b88b65156b6108c1af6febdbbd8e52ae8c7035b0f9609943a735a36a19d43391"

# Connect to Elasticsearch with SSL certificate verification disabled
client = Elasticsearch("https://localhost:9200", api_key=(os.environ.get("ELASTIC_API_KEY")), verify_certs=False)

response = requests.get(url, timeout=120)

if response.status_code == 200:
    data = response.json()
    documents = []
    for item in data:
        index_metadata = {
            "index": {
                "_index": "search-teams_stat_v1",
                "_id": item["team_key"]
            }
        }
        documents.append(index_metadata)
        documents.append(item)

    try:
        print(client.bulk(operations=documents, pipeline="ent-search-generic-ingestion"))
    except Exception as e:
        print("Failed to ingest data:", e)
else:
    print(f"Request failed with status code {response.status_code}")