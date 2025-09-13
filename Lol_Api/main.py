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

# Funkce ktera prevede puuid na level a ikonu
def get_summoners_level(puuid):
    api_url1 = "https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/" + puuid
    api_url1 = api_url1 + '?api_key=' + API_KEY
    response = requests.get(api_url1)
    summoners_name = str(response.json()['profileIconId'])
    summoners_level = str(response.json()['summonerLevel'])

    return summoners_name, summoners_level

def print_user_info(summoners_name, summoners_level, puuid):
    print("Ikona: " + summoners_name)
    print("Level: " + summoners_level)
    print("puuid: " + puuid)


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

def get_champions_info_by_puuid():
    puuid = input("Enter Puuid: ")
    api_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/" + puuid
    api_url = api_url + '?api_key=' + API_KEY
    response = requests.get(api_url)
    summoners_name = str(response.json()['gameName'])
    summoners_tag = str(response.json()['tagLine'])
    print("Summoner name: " + summoners_name)
    print("Summoner tag: " + summoners_tag)

    
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
        summoners_name, summoners_level, = get_summoners_level(puuid)
        print_user_info(summoners_name, summoners_level, puuid)
        
    elif user_input == "2":
        get_free_champions()

    #elif user_input == "3":
        # LeagueV4
    
    elif user_input == "4":
        get_champions_info_by_puuid()
    
    elif user_input == "5":
        puuid = input("Enter one summoners puuid from the clash team: ")
        clash_url = "https://eun1.api.riotgames.com/lol/clash/v1/players/by-puuid/" + puuid
        clash_url = clash_url + '?api_key=' + API_KEY
        response = requests.get(clash_url)
        teamid = response.json()[0]["teamId"]
        clash_url_team = "https://eun1.api.riotgames.com/lol/clash/v1/teams/" + str(teamid)
        clash_url_team = clash_url_team + '?api_key=' + API_KEY
        response = requests.get(clash_url_team)
        print("Clash team name: " + str(response.json()['name']))
        print("Players in the team and their positions: " + str(response.json()['players']))

    elif user_input == "x":
        break
    
    else:
        print("Wrong input")

    
