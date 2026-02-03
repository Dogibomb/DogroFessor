from api_key import API_KEY
import requests
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from cache import *

##------------------- GET SUMMONERS LEVEL ------------------##

def get_summoners_level(puuid, region):
    region = region.lower()
    if region == "eune":
        region = "eun1"
    if region == "br":
        region = "br1"
    if region == "na":
        region = "na1"
    if region == "eune":
        region = "eun1"
    if region == "lan":
        region = "la1"
    if region == "las":
        region = "la2"
    if region == "oce":
        region = "oc1"
    if region == "tr":
        region = "tr1"
    if region == "jp":
        region = "jp1"

    key = f"summoner_{puuid}_{region}"
    cached = get_from_cache(key)
    if cached:
        return cached["icon"], cached["level"], cached["rank"]
    
    api_url1 = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/" + puuid
    api_url1 = api_url1 + '?api_key=' + API_KEY
    api_url2 = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/" + puuid
    api_url2 = api_url2 + '?api_key=' + API_KEY
    
    try:
        response_rank = requests.get(api_url2)
        response_level = requests.get(api_url1)

        if response_level.status_code != 200:
            data = response_level.json()
            if "status" in data and "status_code" in data["status"]:
                print("Error:", data["status"]["status_code"])
            else:
                print("Error:", response_level.status_code)
            return None

        if response_rank.status_code != 200:
            print("Error:", response_rank.json()["status"]["status_code"])
            return (response_level.json().get('profileIconId', 0),
                    response_level.json().get('summonerLevel', 0),
                    [])

        data_level = response_level.json()
        data_rank = response_rank.json()

        if "status" in data_level or "status" in data_rank:
            print(f"[API ERROR] get_summoners_level: {data_level.get('status', data_rank.get('status'))}")
            return None

        summoners_icon = str(response_level.json()['profileIconId'])
        summoners_level = str(response_level.json()['summonerLevel'])
        summoners_rank = response_rank.json()

        set_to_cache(key, {
            "icon": summoners_icon,
            "level": summoners_level,
            "rank": summoners_rank,
        })

    except Exception as e:
        print(f"[ERROR] get_summoners_level failed: {e}")
        return None
    
    return summoners_icon, summoners_level, summoners_rank

def calculate_winrate(summoners_rank):
    ranked_info_solo = next((q for q in summoners_rank if q["queueType"] == "RANKED_SOLO_5x5"), None)
    ranked_info_flex = next((q for q in summoners_rank if q["queueType"] == "RANKED_FLEX_SR"), None)

    if ranked_info_solo:
        wins_solo = ranked_info_solo["wins"]
        losses_solo = ranked_info_solo["losses"]
        winrate_solo = round((wins_solo / (wins_solo + losses_solo)) * 100)
    else:
        winrate_solo = 0

    if ranked_info_flex:
        wins_flex = ranked_info_flex["wins"]
        losses_flex = ranked_info_flex["losses"]
        winrate_flex = round((wins_flex / (wins_flex + losses_flex)) * 100)
    else:
        winrate_flex = 0

    return winrate_solo, winrate_flex

def get_real_ranks(summoners_rank):
    solo_duo_rank = next((q for q in summoners_rank if q["queueType"] == "RANKED_SOLO_5x5"), None)
    flex_rank = next((q for q in summoners_rank if q["queueType"] == "RANKED_FLEX_SR"), None)
    try:
        real_solo_duo_rank = str(solo_duo_rank["tier"]) + " " + str(solo_duo_rank["rank"])
        lp_solo = solo_duo_rank["leaguePoints"]
        wins_solo = solo_duo_rank["wins"]
        losses_solo = solo_duo_rank["losses"]
    except:
        real_solo_duo_rank = "None rank"
        lp_solo = "None"
        wins_solo = "None"
        losses_solo = "None"
    
    try:
        real_flex_rank = str(flex_rank["tier"]) + " " + str(flex_rank["rank"])
        lp_flex = flex_rank["leaguePoints"]
        wins_flex = flex_rank["wins"]
        losses_flex = flex_rank["losses"]
    except:
        real_flex_rank = "None rank"
        lp_flex = "None"
        wins_flex = "None"
        losses_flex = "None"

    return real_flex_rank, real_solo_duo_rank, lp_flex, lp_solo, wins_flex, wins_solo, losses_flex, losses_solo

#------------------- GET CHAMPIONS INFO BY PUUID WITHOUT INPUT ------------------##

def get_champions_info_by_puuid_without_input(puuid):
    api_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/" + puuid
    api_url = api_url + '?api_key=' + API_KEY
    response = requests.get(api_url)

    if response.status_code != 200:
        print("Error:", response.json()["status"]["status_code"])
        print("Invalid puuid")
        return None

    data = response.json()
    summoners_name = data.get('gameName')
    summoners_tag = data.get('tagLine')

    return summoners_name, summoners_tag

#------------------- GET PUUID ------------------##



def get_puuid(name, tag):
    key = f"puuid_{name}#{tag}"
    cached = get_from_cache(key)
    if cached:
        return cached

    puuid_url_finder = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}"
    response = requests.get(puuid_url_finder)

    if response.status_code == 200:
        data = response.json()
        puuid = data["puuid"]
        set_to_cache(key, puuid)
        return puuid
    elif response.status_code == 401:
        # špatný/expirující API klíč
        msg = QMessageBox()
        msg.setWindowTitle("API Key Error")
        msg.setText("❌ Your API key is invalid or expired.")
        msg.setStyleSheet("background-color: #2D3848; color: white; font-size: 18px;")
        msg.exec_()
        return None
    elif response.status_code == 404:
        # špatný summoner
        msg = QMessageBox()
        msg.setWindowTitle("Summoner Not Found")
        msg.setText("❌ Could not find summoner with that Name#Tag.")
        msg.setStyleSheet("background-color: #2D3848; color: white; font-size: 18px;")
        msg.exec_()
        return None
    else:
        # ostatní chyby
        msg = QMessageBox()
        msg.setWindowTitle("HTTP Error")
        msg.setText(f"❌ Request failed with status code {response.status_code}")
        msg.setStyleSheet("background-color: #2D3848; color: white; font-size: 18px;")
        msg.exec_()
        return None

    
    
    
def get_icon(icon):
    url = f"https://ddragon.leagueoflegends.com/cdn/15.18.1/img/profileicon/{icon}.png"
    response = requests.get(url)
    if response.status_code == 200:
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        return pixmap
    return None

def check_what_rank(rank):
    if not rank:
        return "unranked.png"

    rank = rank.lower()

    if "iron" in rank:
        return "iron.png"
    if "bronze" in rank:
        return "bronze.png"
    if "silver" in rank:
        return "silver.png"
    if "gold" in rank:
        return "gold.png"
    if "platinum" in rank:
        return "platinum.png"
    if "emerald" in rank:
        return "emerald.png"
    if "diamond" in rank:
        return "diamond.png"
    if "master" in rank and "grand" not in rank:
        return "master.png"
    if "grandmaster" in rank:
        return "grandmaster.png"
    if "challenger" in rank:
        return "challenger.png"