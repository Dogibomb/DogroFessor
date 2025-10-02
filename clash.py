import requests
from user import get_champions_info_by_puuid_without_input, get_puuid
from api_key import API_KEY

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