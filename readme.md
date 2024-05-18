# Env Setup
1. Install docker and docker compose on your local machine
2. Create .env file inside `docker-elk-official/` to create password for elastic and kibana using this <a href="https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#docker-compose-file">reference</a>
3. Start ELK using command `docker compose up -d`
4. Create virtual environment and install the required modules using `pip install -r requirements`
5. You also need to create .env file in the root folder with the following configuration:
```
FOOTBALL_API_KEY=<your-footballapi.com-api-key>
ELASTIC_API_KEY=<your-elastic-api-key>
```

# Ingestion
There are two version of ingestion with different index mapping. Index version 1 using implicit mapping and index version 2 using explicit mapping so you need to create mapping for index version 2 before ingest the data.

1. Create explicit mapping for index 2 with name: `footballapi.com-events-statistics-v2`. You can go to dev tools on Kibana and create following API request:
```
PUT /footballapi.com-events-statistics-v2
<JSON from mappings/match-v2.json>
```

2. You can then execute daily_ingestion_v1.py and daily_ingestion_v2.py to ingest to index version 1 and version 2 respectively. Make sure you have valid API KEY to connect to footballapi.com.

3. You can set the ingestion period inside the scripts.

4. Use team_stat.py to add new index for team_statistic, the index should have 16 team entry in it. example index name:
```
index="search-teams_stat_v1"
```
After you run the script before, now run update_team_stat.py to append more detailed data for each team

# API
1. You can start the API by going under `app/` folder and execute `python app.py`
2. You can access the front end on http://localhost:5000/

# Streamlit
1. Go to app/streamlit.py
2. For each section such as : Head-to-Head, Team_Stat and Player_stat, add the code to each function respectively
```
def head_to_head():
    st.header("Head to Head")
    # Add your code for the Head to Head page here

def player_analysis():
    st.header("Player Analysis")
    # Add your code for the Player Analysis page here
```
3. We can choose what team to be shown from dropdown menu provided in Team Analysis page

# Machine Learning
1. The machine learning model in Team Analysis used to forecast team Goal Difference. The model use ARIMA method to forecast