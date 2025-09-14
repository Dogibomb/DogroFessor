from api_key import API_KEY
import requests

# Funkce ktera prevede jmeno na puuid
def get_puuid():
    name = input("Enter your summoner name: ")
    hash_tag = input("Enter your hash tag: ")
    puuid_url_finder = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/" + name + "/" + hash_tag
    puuid_url_finder = puuid_url_finder + '?api_key=' + API_KEY
    response = requests.get(puuid_url_finder)
    puuid = response.json()['puuid']

    return puuid

# Funkce ktera prevede puuid na level a ikonu, rank ...
def get_summoners_level(puuid):
    api_url1 = "https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/" + puuid
    api_url1 = api_url1 + '?api_key=' + API_KEY
    api_url2 = "https://eun1.api.riotgames.com/lol/league/v4/entries/by-puuid/" + puuid
    api_url2 = api_url2 + '?api_key=' + API_KEY
    response_rank = requests.get(api_url2)
    response_level = requests.get(api_url1)
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
    free_champions = response.json()

    for i in free_champions['freeChampionIds']:
        for key, value in champions.items():
            if int(value['key']) == i:
                print(value['name'])

def get_champions_info_by_puuid_without_input(puuid):
    api_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/" + puuid
    api_url = api_url + '?api_key=' + API_KEY
    response = requests.get(api_url)
    summoners_name = str(response.json()['gameName'])
    summoners_tag = str(response.json()['tagLine'])

    return summoners_name, summoners_tag

def get_champions_info_by_puuid():
    puuid = input("Enter Puuid: ")
    api_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/" + puuid
    api_url = api_url + '?api_key=' + API_KEY
    response = requests.get(api_url)
    summoners_name = str(response.json()['gameName'])
    summoners_tag = str(response.json()['tagLine'])
    print("Summoner name: " + summoners_name)
    print("Summoner tag: " + summoners_tag)

def clash_info():
    puuid = input("Enter one summoner puuid from the clash team: ")
    clash_url = "https://eun1.api.riotgames.com/lol/clash/v1/players/by-puuid/" + puuid
    clash_url = clash_url + '?api_key=' + API_KEY
    response = requests.get(clash_url)
    teamid = response.json()[0]["teamId"]
    clash_url_team = "https://eun1.api.riotgames.com/lol/clash/v1/teams/" + str(teamid)
    clash_url_team = clash_url_team + '?api_key=' + API_KEY
    response = requests.get(clash_url_team)

    print("Clash team name: " + str(response.json()['name']))
    print("Players in the team and their positions: ")

    for player in response.json()['players']:
        player_puuid = player["puuid"]
        summoners_name, summoners_tag = get_champions_info_by_puuid_without_input(player_puuid)
        print(f"- {summoners_name}#{summoners_tag} | Position: {player['position']} | Role: {player['role']}")


champions = get_champions_info()



user_input = ''

while(True):
    
    print("-------------------------------")

    print("Information table about Lol")
    print("For Summoner info press 1")
    print("For Free Champion info press 2")
    print("For LeagueV4 press 3")
    print("For Convert puuid to name press 4")
    print("For Clash info press 5")
    print("To exit press x")

    print("-------------------------------")

    user_input = input("Enter your choice: ")

    print("-------------------------------")

    if user_input == "1":
        puuid = get_puuid()
        summoners_name, summoners_level, summoners_rank = get_summoners_level(puuid)
        print_user_info(summoners_name, summoners_level, puuid, summoners_rank)
        
    elif user_input == "2":
        get_free_champions()

    #elif user_input == "3":
        # LeagueV4
    
    elif user_input == "4":
        get_champions_info_by_puuid()
    
    elif user_input == "5":
        clash_info()

    elif user_input == "x":
        break
    
    else:
        print("Wrong input")

    
