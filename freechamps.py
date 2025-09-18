from api_key import API_KEY
import requests

def get_champions_info():
    champion_url = "https://ddragon.leagueoflegends.com/cdn/15.18.1/data/en_US/champion.json"
    response = requests.get(champion_url)
    champions = response.json()['data']

    champions = {int(info['key']): info['name'] for info in champions.values()}
    return champions

def get_free_champions():
    champions = get_champions_info()
    free_champions_url = "https://eun1.api.riotgames.com/lol/platform/v3/champion-rotations"
    free_champions_url = free_champions_url + '?api_key=' + API_KEY
    response = requests.get(free_champions_url)

    if response.status_code != 200:
        print("Error:", response.json()["status"]["status_code"])
        return None

    free_champions = response.json()

    print("Free champion rotation:")
    count = 0
    for champ_id in free_champions['freeChampionIds']:
        if count == 5:
            print("\n", end="")
            count += 1
            count = 0
        else:
            print("-", champions.get(champ_id, f"Unknown ({champ_id})"), end=", ")
            count += 1
        