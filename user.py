from api_key import API_KEY
import requests

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

##------------------- GET SUMMONERS LEVEL ------------------##

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

##------------------- PRINT USER INFO ------------------##

def print_user_info(summoners_name, summoners_level, puuid , summoners_rank):
    print("Ikona: " + summoners_name)
    print("Level: " + summoners_level)
    print("puuid: " + puuid)

    solo_duo_rank = next((q for q in summoners_rank if q["queueType"] == "RANKED_SOLO_5x5"), None)
    flex_rank = next((q for q in summoners_rank if q["queueType"] == "RANKED_FLEX_SR"), None)

    real_solo_duo_rank = solo_duo_rank["queueType"] + " " + str(solo_duo_rank["tier"]) + " " + str(solo_duo_rank["rank"]) + " " + str(solo_duo_rank["leaguePoints"])
    real_flex_rank = flex_rank["queueType"] + " " + str(flex_rank["tier"]) + " " + str(flex_rank["rank"]) + " " + str(flex_rank["leaguePoints"])

    print("Rank in Solo/Duo: " + str(real_solo_duo_rank))
    print("Rank in Flex: " + str(real_flex_rank))

#------------------- GET CHAMPIONS INFO BY PUUID WITHOUT INPUT ------------------##

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

#------------------- GET PUUID ------------------##

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