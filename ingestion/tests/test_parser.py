from football_parser import parse_player_stats
import json

def test_player():
    x = """{
        "player_name": "Mark Flekken",
        "player_key": "2076522167",
        "player_number": "1",
        "player_position": "Goalkeepers",
        "player_isCaptain": "False",
        "player_isSubst": "True",
        "player_total_shots": "0",
        "player_shots_on_goal": "0",
        "player_goals": "0",
        "player_goals_conceded": "2",
        "players_minus_goals": "2",
        "player_assists": "0",
        "player_offsides": "0",
        "player_fouls_drawn": "",
        "player_fouls_commited": "0",
        "player_tackles": "0",
        "player_blocks": "0",
        "player_total_crosses": "0",
        "player_acc_crosses": "0",
        "player_interceptions": "0",
        "player_clearances": "2",
        "player_dispossesed": "0",
        "player_saves": "3",
        "player_punches": "0",
        "player_saves_inside_box": "1",
        "player_duels_total": "2",
        "player_duels_won": "1",
        "player_aerials_won": "0",
        "player_dribble_attempts": "1",
        "player_dribble_succ": "1",
        "player_dribbled_past": "1",
        "player_yellow_cards": "0",
        "player_red_cards": "0",
        "player_pen_score": "0",
        "player_pen_miss": "0",
        "player_pen_save": "0",
        "player_pen_committed": "0",
        "player_pen_won": "0",
        "player_hit_woodwork": "0",
        "player_passes": "35",
        "player_passes_acc": "22",
        "player_key_passes": "0",
        "player_minutes_played": "96",
        "player_rating": "7"
    }"""

    y = json.loads(x)

    assert parse_player_stats(y) == {'player_name': 'Mark Flekken', 'player_key': '2076522167', 'player_number': '1', 'player_position': 'Goalkeepers', 'player_isCaptain': False, 'player_isSubst': True, 'player_total_shots': 0, 'player_shots_on_goal': 0, 'player_goals': 0, 'player_goals_conceded': 2, 'players_minus_goals': 2, 'player_assists': 0, 'player_offsides': 0, 'player_fouls_drawn': 0, 'player_fouls_commited': 0, 'player_tackles': 0, 'player_blocks': 0, 'player_total_crosses': 0, 'player_acc_crosses': 0, 'player_interceptions': 0, 'player_clearances': 2, 'player_dispossesed': 0, 'player_saves': 3, 'player_punches': 0, 'player_saves_inside_box': 1, 'player_duels_total': 2, 'player_duels_won': 1, 'player_aerials_won': 0, 'player_dribble_attempts': 1, 'player_dribble_succ': 1, 'player_dribbled_past': 1, 'player_yellow_cards': 0, 'player_red_cards': 0, 'player_pen_score': 0, 'player_pen_miss': 0, 'player_pen_save': 0, 'player_pen_committed': 0, 'player_pen_won': 0, 'player_hit_woodwork': 0, 'player_passes': 35, 'player_passes_acc': 22, 'player_key_passes': 0, 'player_minutes_played': 96, 'player_rating': 7}