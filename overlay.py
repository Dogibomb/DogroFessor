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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_player_data(player):
            name = player['riotIdGameName']
            tag = player['riotIdTagLine']
            champ_name = player["championName"]
            summonername = player["summonerName"]
            team = player["team"]

            if not name or not tag or "Bot" in summonername:
                return {
                    "name": summonername,
                    "tag": "",
                    "team": team,
                    "champ": champ_name,
                    "summname": summonername,
                    "rank": "BOT"
                }

            puuid = get_puuid(name, tag)
            if not puuid:
                return {
                    "name": name,
                    "tag": tag,
                    "team": team,
                    "champ": champ_name,
                    "summname": summonername,
                    "rank": "UNRANKED"
                }
            
            result = get_summoners_level(puuid, region="EUNE")
            if not result:
                return {
                    "name": name,
                    "tag": tag,
                    "team": team,
                    "champ": champ_name,
                    "summname": summonername,
                    "rank": "UNRANKED"
                }
            
            icon, level, rank = result

            real_flex_rank, real_solo_duo_rank, *_ = get_real_ranks(rank)

            return {
                "name": name,
                "tag": tag,
                "team": team,
                "champ": champ_name,
                "summname": summonername,
                "rank": real_solo_duo_rank
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
    "monkeyking": "wukong",
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
            results = [f.result() for f in as_completed(futures)]

        try:
            for player_data in results:
                if not player_data:
                    continue
                
                team = player_data["team"]
                champ_name = rename_champs(player_data["champ"])
                summonername = player_data["summname"]
                rank_name = player_data["rank"]
                
                print(champ_name)

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
        main_layout.addLayout(redside)

        self.setLayout(main_layout)
