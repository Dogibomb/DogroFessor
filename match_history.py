from api_key import API_KEY
import requests
import time
from user import get_puuid, get_champions_info_by_puuid_without_input, get_summoners_level

def get_user_normal_match_history():
    puuid = get_puuid()
    api_url_normal_matches = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids?type=normal&start=0&count=5"
    
    response_normal = requests.get(api_url_normal_matches + '&api_key=' + API_KEY)

    if response_normal.status_code != 200:
        print("Error:", response_normal.json()["status"]["status_code"])
        return None
  
    normal_matches = response_normal.json()

    return normal_matches

def get_user_ranked_match_history():
    puuid = get_puuid()
    api_url_ranked_matches = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids?type=ranked&start=0&count=5"

    response_ranked = requests.get(api_url_ranked_matches + '&api_key=' + API_KEY)

    if response_ranked.status_code != 200:
        print("Error:", response_ranked.json()["status"]["status_code"])
        return None
    
    ranked_matches = response_ranked.json()
    
    return ranked_matches

def convert_match_ids(match_ids):
    matchlist = []
    for match_id in match_ids:
        api_url_convertor = "https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id
        response = requests.get(api_url_convertor + '?api_key=' + API_KEY)
        matchlist.append(response.json())
        

    if response.status_code != 200:
        print("Error:", response.json()["status"]["status_code"])
        return None

    count = 0
    player_cache = {}
    for i, match in enumerate(matchlist, start=1):
        count = 0
        time.sleep(0.2)
        print(f"\nMatch {i}:")
        duration = match["info"]["gameDuration"]
        print(f"  Duration: {round(duration/60)} minutes")
        print("  Players:")

        for p in match["info"]["participants"]:
            if count == 5:
                count = 0
                print("\t-----------------------------------")

            puuid = p["puuid"]

            if puuid in player_cache:
                name, tag = player_cache[puuid]
            else:    
                name, tag = get_champions_info_by_puuid_without_input(p["puuid"])
                player_cache[puuid] = (name, tag)

            summoners_name, summoners_level, rank = get_summoners_level(p["puuid"])
            soloq = next((r for r in rank if r['queueType'] == 'RANKED_SOLO_5x5'), None)

            champ = p["championName"]
            kda = f"{p['kills']}/{p['deaths']}/{p['assists']}"
            print(f"    {name} - {soloq['tier']} {soloq['rank']} - {champ} | KDA: {kda}")
            time.sleep(0.2)
            count += 1
