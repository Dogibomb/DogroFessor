from Lol_Api.api_key import API_KEY
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

def print_user_info(summoners_name, summoners_level):
    print("Ikona: " + summoners_name)
    print("Level: " + summoners_level)


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
    





champions = get_champions_info()

print("Information table about Lol")
print("For Summoner info press 1")
print("For Free Champion info press 2")

user_input = ''

while(True):
    user_input = input("Enter your choice: ")

    if user_input == "1":
        puuid = get_puuid()
        summoners_name, summoners_level = get_summoners_level(puuid)
        print_user_info(summoners_name, summoners_level)
        
    elif user_input == "2":
        get_free_champions()

    if user_input == "x":
        break
    
    else:
        print("Wrong input")
