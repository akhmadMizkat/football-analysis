import requests
from elasticsearch import Elasticsearch
import os
import dotenv

dotenv.load_dotenv("../.env")

# Define the URL of the API endpoint
url = "https://apiv3.apifootball.com/?action=get_standings&league_id=152&APIkey=b88b65156b6108c1af6febdbbd8e52ae8c7035b0f9609943a735a36a19d43391"

# Connect to Elasticsearch with SSL certificate verification disabled
client = Elasticsearch("https://localhost:9200", api_key=(os.environ.get("ELASTIC_API_KEY")), verify_certs=False)

# Send a GET request to the API endpoint
response = requests.get(url)

if response.status_code == 200:
    # Parse the JSON response to get the array of data
    data = response.json()
    print("Received data:", data)
    for item in data:
        # Create a new dictionary with only the specified attributes
        filtered_item = {key: item[key] for key in ("overall_league_position", "overall_league_W", "overall_league_D", "overall_league_L", "home_league_W", "home_league_D", "home_league_L", "away_league_W", "away_league_D", "away_league_L")}
        try:
            # Append data to the existing document
            client.update(index="search-teams_stat_v1", id=item["team_id"], body={"doc": filtered_item})
            print(f"Appended data to document with ID {item['team_id']}")
        except Exception as e:
            print(f"Failed to append data to document with ID {item['team_id']}: {e}")
else:
    print(f"Request failed with status code {response.status_code}")