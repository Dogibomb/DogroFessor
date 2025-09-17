from api_key import API_KEY
import requests

# Funkce ktera prevede jmeno na puuid
def get_puuid():
    while True:
        name = input("Enter your summoner name: ")
        hash_tag = input("Enter your hash tag: ")
        puuid_url_finder = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{hash_tag}?api_key={API_KEY}"

        response = requests.get(puuid_url_finder)

        if response.status_code != 200:
            print("Error:", response.json()["status"]["status_code"])
            print("Invalid name/tag")
            continue

        elif response.status_code == 200:
            data = response.json()
            return data["puuid"]
        elif response.status_code == 404:
            print("Error:", response.json()["status"]["status_code"])
            print("Invalid name/tag")
            continue


# Funkce ktera prevede puuid na level a ikonu, rank ...
def get_summoners_level(puuid):
    api_url1 = "https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/" + puuid
    api_url1 = api_url1 + '?api_key=' + API_KEY
    api_url2 = "https://eun1.api.riotgames.com/lol/league/v4/entries/by-puuid/" + puuid
    api_url2 = api_url2 + '?api_key=' + API_KEY
    response_rank = requests.get(api_url2)
    response_level = requests.get(api_url1)

    if response_level.status_code != 200:
        print("Error:", response_level.json()["status"]["status_code"])
        return None

    if response_rank.status_code != 200:
        print("Error:", response_rank.json()["status"]["status_code"])
        return None

    summoners_name = str(response_level.json()['profileIconId'])
    summoners_level = str(response_level.json()['summonerLevel'])
    summoners_rank = response_rank.json()

    return summoners_name, summoners_level, summoners_rank

def print_user_info(summoners_name, summoners_level, puuid , summoners_rank):
    print("Ikona: " + summoners_name)
    print("Level: " + summoners_level)
    print("puuid: " + puuid)

    solo_duo_rank = next((q for q in summoners_rank if q["queueType"] == "RANKED_SOLO_5x5"), None)
    flex_rank = next((q for q in summoners_rank if q["queueType"] == "RANKED_FLEX_SR"), None)

    print("Rank in Solo/Duo: " + str(solo_duo_rank["queueType"]) + " " + str(solo_duo_rank["tier"]) + " " + str(solo_duo_rank["rank"]) + " " + str(solo_duo_rank["leaguePoints"]) + "LP")
    print("Rank in Flex: " + str(flex_rank["queueType"]) + " " + str(flex_rank["tier"]) + " " + str(flex_rank["rank"]) + " " + str(flex_rank["leaguePoints"]) + "LP")


def get_champions_info():
    champion_url = "https://ddragon.leagueoflegends.com/cdn/15.18.1/data/en_US/champion.json"
    response = requests.get(champion_url)
    champions = response.json()['data']

    return champions

def get_free_champions():
    free_champions_url = "https://eun1.api.riotgames.com/lol/platform/v3/champion-rotations"
    free_champions_url = free_champions_url + '?api_key=' + API_KEY
    response = requests.get(free_champions_url)

    if response.status_code != 200:
        print("Error:", response.json()["status"]["status_code"])
        return None

    free_champions = response.json()

    for i in free_champions['freeChampionIds']:
        for key, value in champions.items():
            if int(value['key']) == i:
                print(value['name'])

def get_champions_info_by_puuid_without_input(puuid):
    api_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/" + puuid
    api_url = api_url + '?api_key=' + API_KEY
    response = requests.get(api_url)

    if response.status_code != 200:
        print("Error:", response.json()["status"]["status_code"])
        print("Invalid puuid")
        return None

    summoners_name = str(response.json()['gameName'])
    summoners_tag = str(response.json()['tagLine'])

    return summoners_name, summoners_tag

def get_User_info_by_puuid():
    puuid = input("Enter Puuid: ")
    api_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/" + puuid
    api_url = api_url + '?api_key=' + API_KEY
    response = requests.get(api_url)

    if response.status_code != 200:
        print("Error:", response.json()["status"]["status_code"])
        print("Invalid puuid")
        return None

    summoners_name = str(response.json()['gameName'])
    summoners_tag = str(response.json()['tagLine'])
    print("Summoner name: " + summoners_name)
    print("Summoner tag: " + summoners_tag)

def clash_info():
    puuid = get_puuid()
    clash_url = "https://eun1.api.riotgames.com/lol/clash/v1/players/by-puuid/" + puuid
    clash_url = clash_url + '?api_key=' + API_KEY
    response = requests.get(clash_url)

    if response.status_code != 200:
        print("Error:", response.json()["status"]["status_code"])
        print("This player is not in clash team or invalid name/tag")
        return None

    try:
        teamid = response.json()[0]["teamId"]
    except (KeyError, IndexError):
        print("This player is not in clash team or invalid puuid")
        return None

    clash_url_team = "https://eun1.api.riotgames.com/lol/clash/v1/teams/" + str(teamid)
    clash_url_team = clash_url_team + '?api_key=' + API_KEY
    response = requests.get(clash_url_team)

    if response.status_code != 200:
        print("Error:", response.json()["status"]["status_code"])
        return None

    print("Clash team name: " + str(response.json()['name']))
    print("Players in the team and their positions: ")

    for player in response.json()['players']:
        player_puuid = player["puuid"]
        summoners_name, summoners_tag = get_champions_info_by_puuid_without_input(player_puuid)
        print(f"- {summoners_name}#{summoners_tag} | Position: {player['position']} | Role: {player['role']}")

def get_user_normal_match_history():
    puuid = get_puuid()
    
    api_url_normal_matches = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids?type=normal&start=0&count=20"
    
    response_normal = requests.get(api_url_normal_matches + '&api_key=' + API_KEY)
   


    if response_normal.status_code != 200:
        print("Error:", response_normal.json()["status"]["status_code"])
        return None

    
    normal_matches = response_normal.json()

    return normal_matches

def get_user_ranked_match_history():
    puuid = get_puuid()
    api_url_ranked_matches = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids?type=ranked&start=0&count=20"

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
    for i in range(len(matchlist)):
        print("Match ID: " + str(matchlist[i]["metadata"]["participants"]))

user_input = ''

while(True):
    
    print("-------------------------------")

    print("Information table about Lol")
    print("For Summoner info press 1")
    print("For Clash info press 2")
    print("For User Match History press 3")
    print("For Free Champion info press 4")
    print("For Convert puuid to name press 5")
    print("To exit press x")

    print("-------------------------------")

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
        champions = get_champions_info()
        get_free_champions()
    
    elif user_input == "5":
        get_User_info_by_puuid()

    elif user_input == "x":
        break
    
    else:
        print("Wrong input")

    
