from api_git.api_key import API_KEY
import requests
import time
from user import get_puuid, get_champions_info_by_puuid_without_input, get_summoners_level
from cache import *

def get_user_normal_match_history():
    puuid = get_puuid()
    api_url_normal_matches = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids?type=normal&start=0&count=5"
    
    response_normal = requests.get(api_url_normal_matches + '&api_key=' + API_KEY)

    if response_normal.status_code != 200:
        print("Error:", response_normal.json()["status"]["status_code"])
        return None
  
    normal_matches = response_normal.json()

    return normal_matches

def get_user_ranked_match_history(name, tag):
    puuid = get_puuid(name, tag)
    api_url_ranked_matches = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids?type=ranked&start=0&count=5"

    response_ranked = requests.get(api_url_ranked_matches + '&api_key=' + API_KEY)

    if response_ranked.status_code != 200:
        print("Error:", response_ranked.json()["status"]["status_code"])
        return None
    
    ranked_matches = response_ranked.json()
    
    return ranked_matches

def get_user_match_history(name, tag):
    puuid = get_puuid(name, tag)

    key = f"matches_{puuid}"
    cached = get_from_cache(key)
    if cached:
        return cached

    api_url_matches = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=10"

    response = requests.get(api_url_matches + '&api_key=' + API_KEY)

    if response.status_code != 200:
        print("Error:", response.json()["status"]["status_code"])
        return None
    
    matches = response.json()
    
    set_to_cache(key, matches)

    return matches

def convert_match_ids(match_ids, summoners_name):
    matchlist = []
    for match_id in match_ids:
        key = f"match_{match_id}"
        cached = get_from_cache(key)
        if cached:
            match = cached
        else:
            api_url_convertor = "https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id
            response = requests.get(api_url_convertor + '?api_key=' + API_KEY)

            if response.status_code != 200:
                print("Error:", response.json()["status"]["status_code"])
                continue
            
            match = response.json()
            set_to_cache(key, match)

        matchlist.append(match)
        

    matches_data = []
    for match in matchlist:
        game_duration = round(match["info"]["gameDuration"]/60)
        players = match["info"]["participants"]

        team1 = []
        team2 = []

        for i, p in enumerate(players):
            champ = p["championName"]
            kda = f"{p["kills"]}/{p["deaths"]}/{p["assists"]}"
            nametag = f"{p["riotIdGameName"]}#{p["riotIdTagline"]}"
            player_data = {"champion": champ, "kda":kda, "name": nametag}
            if i < 5:
                team1.append(player_data)
            else:
                team2.append(player_data)
            if p["riotIdGameName"].lower() == summoners_name.lower():
                my_kda = kda    
        matches_data.append({
            "duration": game_duration,
            "team1": team1,
            "team2": team2,
            "name": summoners_name,
            "kda": my_kda,
        })

    return matches_data
    
