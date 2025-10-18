import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QShortcut, QHBoxLayout
from PyQt5.QtGui import QKeySequence, QPixmap
from PyQt5.QtCore import Qt
from imports import resource_path, standardize_icon
from organization import make_shadow
import urllib3
import requests
from user import get_summoners_level, get_puuid, get_real_ranks, check_what_rank
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from api_key import API_KEY_OPENAI

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_player_data(player):
            name = player['riotIdGameName']
            tag = player['riotIdTagLine']
            champ_name = player["championName"]
            summonername = player["summonerName"]
            team = player["team"]
            lane = player.get("position", "UNKNOWN")

            if not name or not tag or "Bot" in summonername:
                return {
                    "name": summonername,
                    "tag": "",
                    "team": team,
                    "champ": champ_name,
                    "summname": summonername,
                    "rank": "BOT",
                    "lane": lane
                }

            puuid = get_puuid(name, tag)
            if not puuid:
                return {
                    "name": name,
                    "tag": tag,
                    "team": team,
                    "champ": champ_name,
                    "summname": summonername,
                    "rank": "UNRANKED",
                    "lane": lane
                }
            
            result = get_summoners_level(puuid, region="EUNE")
            if not result:
                return {
                    "name": name,
                    "tag": tag,
                    "team": team,
                    "champ": champ_name,
                    "summname": summonername,
                    "rank": "UNRANKED",
                    "lane": lane
                }
            
            icon, level, rank = result

            real_flex_rank, real_solo_duo_rank, *_ = get_real_ranks(rank)

            return {
                "name": name,
                "tag": tag,
                "team": team,
                "champ": champ_name,
                "summname": summonername,
                "rank": real_solo_duo_rank,
                "lane": lane
            }

def get_realtime_data():
    try:
        data = requests.get(
            "https://127.0.0.1:2999/liveclientdata/allgamedata",
            verify=False, timeout=2
        ).json()
        return data
    except Exception as e:
        print("Error fetching data:", e)
        return None

CHAMPION_ALIASES = {
    "wukong": "monkeyking",
    "renataglasc": "renata",
    "nunuwillump": "nunu",
    "belveth": "belveth",
    "chogath": "chogath",
    "kogmaw": "kogmaw",
    "leblanc": "leblanc",
    "drmundo": "drmundo",
    "jarvaniv": "jarvaniv",
    "xinzhao": "xinzhao",
}

def rename_champs(champ_name):
    if isinstance(champ_name, set):
        champ_name = next(iter(champ_name))

    clean = (
        champ_name.lower()
        .replace(" ", "")
        .replace("'", "")
        .replace(".", "")
        .replace("&", "and")
    )

    return CHAMPION_ALIASES.get(clean, clean)

responses_cache = {}

class Overlay(QWidget):
    def __init__(self):
        super().__init__()

        data = get_realtime_data()
        if not data:
            print("no game")
            return

        self.setObjectName("Overlay")

        with open(resource_path("styles.qss"), "r") as f:
            self.setStyleSheet(f.read())

        self.setFixedSize(1200, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        main_layout = QHBoxLayout(self)

        redside = QVBoxLayout()
        blueside = QVBoxLayout()
        players = data["allPlayers"]

        # vytvoř pool s 8 vlákny
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(fetch_player_data, p) for p in players]
            results = [f.result() for f in futures]

        def find_opponent(player):
            if player["lane"] == "UNKNOWN":
                return None
            opposite_team = blue_team if player["team"] == "CHAOS" else red_team
            for opp in opposite_team:
                if opp["lane"] == player["lane"]:
                    return opp["champ"]
            return None

        red_team = [p for p in results if p["team"] == "CHAOS"]
        blue_team = [p for p in results if p["team"] == "ORDER"]

        local_player = data.get("activePlayer", {}).get("summonerName", None)
        active_data = next((p for p in results if p["summname"] == local_player), None)
        team = active_data["team"]
        active_lane = active_data["lane"]
        active_champ = rename_champs(active_data["champ"])
        opponent = find_opponent(active_data)

        latest_patch = "25.20"
        matchup_key = f"{active_champ}_vs_{opponent}"

        if matchup_key in responses_cache:
            response_text = responses_cache[matchup_key]
        else:
            client = OpenAI(api_key=API_KEY_OPENAI)
            prompt = f"""
                You are an **expert League of Legends coach**. Produce a **lane-specific guide** in **plain text**. 
                Do NOT use JSON. Make it clear and readable for a human player.

                INPUT VARIABLES:
                - Champion: {active_champ}
                - Opponent: {opponent or "unknown"}
                - Patch: {latest_patch}

                REQUIREMENTS:
                1. Include sections: Build, Runes, Skill Order, Power Spikes, Matchup Notes, Counterplay Tips.
                2. Keep it concise, 150-250 words.
                3. Provide actionable tips for early, mid, and late game.
                4. If opponent is unknown, produce a generic lane guide.
                5. Use standard champion names (e.g., "Wukong", "Renata").

                FORMAT EXAMPLE:

                Champion: Darius
                Opponent: Garen

                Build:
                - Starting items: Doran's Blade, Health Potion
                - Core items: Stridebreaker, Sterak's Gage, Black Cleaver
                - Boots: Plated Steelcaps
                - Optional items: Death's Dance, Guardian Angel

                Runes: Primary: Conqueror, Secondary: Resolve, Shards: Attack Speed, Adaptive Force, Armor

                Skill Order: Q > E > W > Q > Q > R ...

                Power Spikes: Level 3 (Q+E), Level 6 (Ultimate), After completing Stridebreaker

                Matchup Notes: Avoid extended trades early, Garen can all-in if he gets level advantage.

                Counterplay Tips: Don't overextend, bait Garen into tower, dodge his Q, track jungle pressure.

                Now produce a guide for Champion: {active_champ}, Opponent: {opponent or "unknown"}, Lane: {active_lane}, Patch: {latest_patch}.
                """
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional LoL coach."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=800,
            )

            response_text = response.choices[0].message.content
            responses_cache[matchup_key] = response_text
            
        guidelbl = QLabel(response_text)
        guidelbl.setFixedHeight(600)
        guidelbl.setFixedWidth(650)
        guidelbl.setObjectName("guide")
        guidelbl.setWordWrap(True)

        try:
            for player_data in results:
                if not player_data:
                    continue
                
                

                team = player_data["team"]
                champ_name = rename_champs(player_data["champ"])
                lane = player_data["lane"]
                summonername = player_data["summname"]
                rank_name = player_data["rank"]
                opponent = find_opponent(player_data)

                icon_path = (resource_path(f"icons/{champ_name}.png"))
                pixlbl = QLabel()
                pix = QPixmap(icon_path)
                pix = pix.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                pix = standardize_icon(pix, 80)
                pixlbl.setPixmap(pix)
                
                
                ranklbl = QLabel()

                rank_icon_file = check_what_rank(rank_name) if rank_name else "unranked.png"

                if not rank_icon_file or not os.path.exists(resource_path(f"ranky/{rank_icon_file}")):
                    rank_icon_file = "unranked.png"

                pixrank = QPixmap(resource_path(f"ranky/{rank_icon_file}"))
                pixrank = pixrank.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                pixrank = standardize_icon(pixrank, 50)
                ranklbl.setPixmap(pixrank)
                ranklbl.setObjectName("rank")
                
                summonernamelbl = QLabel(summonername, self)
                summonernamelbl.setFixedWidth(150)
                summonernamelbl.setObjectName("summname")
                summonernamelbl.setAlignment(Qt.AlignCenter)
                
                info = QVBoxLayout()
                info.addWidget(summonernamelbl)
                info.addWidget(ranklbl)
                
                info.setContentsMargins(0, 0, 0, 0)

                player_row = QHBoxLayout()
                if team == "CHAOS":
                    
                    player_row.addLayout(info)
                    player_row.addWidget(pixlbl)
                    redside.addLayout(player_row)
                else:
                    player_row.addWidget(pixlbl)
                    player_row.addLayout(info)
                    blueside.addLayout(player_row)
        except KeyError:
            print("keyerror bro")

        redside.setAlignment(Qt.AlignLeft)
        blueside.setAlignment(Qt.AlignRight)
        player_row.setObjectName("playerrow")
        player_row.setContentsMargins(0,0,0,0)
        redside.setContentsMargins(0, 0, 20, 0)
        blueside.setContentsMargins(20, 0, 0, 0)
        main_layout.setContentsMargins(0,0,0,0)

        main_layout.addLayout(blueside)
        main_layout.addStretch(1)
        main_layout.addWidget(guidelbl)
        main_layout.addStretch(1)
        main_layout.addLayout(redside)

        self.setLayout(main_layout)

    
