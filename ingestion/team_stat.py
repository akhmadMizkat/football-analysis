import requests
import json
from elasticsearch import Elasticsearch

url = "https://apiv3.apifootball.com/?action=get_teams&league_id=152&APIkey=b88b65156b6108c1af6febdbbd8e52ae8c7035b0f9609943a735a36a19d43391"

# Connect to Elasticsearch with SSL certificate verification disabled
client = Elasticsearch("https://localhost:9200", api_key=("FS_3j44BzwJTVWm0LVLl", "32Gr3iKaRUSky6xgi-td2w"), verify_certs=False)

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("Received data:", data)
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
        client.bulk(operations=documents, pipeline="ent-search-generic-ingestion")
        print("Ingested data into Elasticsearch")
    except Exception as e:
        print("Failed to ingest data:", e)
else:
    print(f"Request failed with status code {response.status_code}")