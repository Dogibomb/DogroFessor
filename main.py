from api_key import API_KEY
import requests
from clash import clash_info
from user import get_User_info_by_puuid, get_summoners_level, print_user_info, get_champions_info_by_puuid_without_input, get_puuid
from freechamps import get_champions_info, get_free_champions

def get_user_normal_match_history():
    puuid = get_puuid()
    
    api_url_normal_matches = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids?type=normal&start=0&count=10"
    
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

def convert_match_ids(match_ids):
    matchlist = []
    for match_id in match_ids:
        api_url_convertor = "https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id
        response = requests.get(api_url_convertor + '?api_key=' + API_KEY)
        matchlist.append(response.json())
        

    if response.status_code != 200:
        print("Error:", response.json()["status"]["status_code"])
        return None

    
    #participants, gameDuration
    count = 0
    for i, match in enumerate(matchlist, start=0):
        print(f"Match {i+1}:")
        players = match["metadata"]["participants"]
        print("Players in the match:")
        for player in players:
            summoners_info = get_champions_info_by_puuid_without_input(player)
            summoners_rank = get_summoners_level(player)
            
            solo_duo_rank = next((q for q in summoners_rank if q["queueType"] == "RANKED_SOLO_5x5"), None)

            print(f"- {summoners_info[0]}#{summoners_info[1]} | Rank: {solo_duo_rank["tier"]} {solo_duo_rank["rank"]}")
            count = 0


user_input = ''

while(True):
    
    print("\n-------------------------------")

    print("DogoPedia - League of Legends API")
    print("For Summoner info press 1")
    print("For Clash info press 2")
    print("For User Match History press 3")
    print("For Free Champion info press 4")
    print("For Convert puuid to name press 5")
    print("To exit press x")

    print("-------------------------------\n")

    user_input = input("Enter your choice: ")

    print("-------------------------------")

    if user_input == "1":
        puuid = get_puuid()
        summoners_name, summoners_level, summoners_rank = get_summoners_level(puuid)
        print_user_info(summoners_name, summoners_level, puuid, summoners_rank)
        
    elif user_input == "2":
        clash_info()
    elif user_input == "3":
        convert_match_ids(get_user_normal_match_history())
    elif user_input == "4":
        get_free_champions()
    elif user_input == "5":
        get_User_info_by_puuid()
    elif user_input == "x":
        break
    else:
        print("Wrong input")