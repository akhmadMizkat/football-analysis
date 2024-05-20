import json
import re
def digit(d):
    return re.sub(r'\D', '', d)

def type_parser(schema, d):
    for k in schema:
        if k not in d:
            if schema[k] == int or schema[k] == float:
                d[k] = 0
            elif schema[k] == str:
                d[k] = ''
            elif schema[k] == digit:
                d[k] = '0'
            elif schema[k] == bool:
                d[k] = False
        
        if (schema[k] == int or schema[k] == float) and d[k] == "":
            d[k] = '0'
        elif schema[k] == bool and d[k].lower() == "false":
            d[k] = 0
        d[k] = schema[k](d[k])
    return d

def parse_statistics(s):
    schema = {
        "team_position": str,
        "team_id": str,
        "team_name": str,
        "throw_in": int,
        "free_kick": int,
        "goal_kick": int,
        "penalty": int,
        "substitution": int,
        "attacks": int,
        "dangerous_attacks": int,
        "on_target": int,
        "off_target": int,
        "shots_total": int,
        "shots_on_goal": int,
        "shots_off_goal": int,
        "shots_blocked": int,
        "shots_inside_box": int,
        "shots_outside_box": int,
        "fouls": int,
        "corners": int,
        "offsides": int,
        "ball_possession": digit,
        "yellow_cards": int,
        "saves": int,
        "passes_total": int,
        "passes_accurate": int
    }
    return type_parser(schema, s)

def parse_player_stats(p):
    schema = {
        "player_name": str,
        "player_key": str,
        "player_number": str,
        "player_position": str,
        "player_isCaptain": bool,
        "player_isSubst": bool,
        "player_total_shots": int,
        "player_shots_on_goal": int,
        "player_goals": int,
        "player_goals_conceded": int,
        "players_minus_goals": int,
        "player_assists": int,
        "player_offsides": int,
        "player_fouls_drawn": int,
        "player_fouls_commited": int,
        "player_tackles": int,
        "player_blocks": int,
        "player_total_crosses": int,
        "player_acc_crosses": int,
        "player_interceptions": int,
        "player_clearances": int,
        "player_dispossesed": int,
        "player_saves": int,
        "player_punches": int,
        "player_saves_inside_box": int,
        "player_duels_total": int,
        "player_duels_won": int,
        "player_aerials_won": int,
        "player_dribble_attempts": int,
        "player_dribble_succ": int,
        "player_dribbled_past": int,
        "player_yellow_cards": int,
        "player_red_cards": int,
        "player_pen_score": int,
        "player_pen_miss": int,
        "player_pen_save": int,
        "player_pen_committed": int,
        "player_pen_won": int,
        "player_hit_woodwork": int,
        "player_passes": int,
        "player_passes_acc": int,
        "player_key_passes": int,
        "player_minutes_played": int,
        "player_rating": int
    }

    return type_parser(schema, p)

def parse_lineup(p):
    schema = {
        "team_position": str,
        "player_team_id": str,
        "player_team_name": str,
        "lineup_player": str,
        "lineup_number": str,
        "lineup_position": str,
        "player_key": str,
        "player_name": str,
        "status": str
    }

    return type_parser(schema, p)

    
