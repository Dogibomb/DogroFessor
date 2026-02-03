import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QShortcut, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QKeySequence, QPixmap
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG
from imports import resource_path, standardize_icon
from organization import make_shadow
import urllib3
import requests
from user import get_summoners_level, get_puuid, get_real_ranks, check_what_rank
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from api_key import API_KEY_OPENAI
import re
from bs4 import BeautifulSoup
from cache import load_cache, save_cache, get_from_cache, set_to_cache
from playwright.sync_api import sync_playwright

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

            key = f"{name}#{tag}"

            cached_rank = get_from_cache(key)
            if cached_rank:
                return {
                    "name": name,
                    "tag": tag,
                    "team": team,
                    "champ": champ_name,
                    "summname": summonername,
                    "rank": cached_rank,
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

            set_to_cache(key, real_solo_duo_rank)

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

def search_build(active_champ, active_lane):

    key = f"{active_champ}_{active_lane}"

    cached = get_from_cache(key)
    if cached:
        return cached  

    WANTED_SECTIONS = ["spells", "items", "situational items"]
    build_data = {}

    if active_lane is None:
        URL = f"https://mobalytics.gg/lol/champions/{active_champ}/build/{active_lane}"
    else:
        URL = f"https://mobalytics.gg/lol/champions/{active_champ}/build/"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_load_state("networkidle")

        boxes = page.locator("div.m-owe8v3").all()

        for box in boxes:
            h3 = box.locator("h3").first
            if not h3.count(): continue
            section_title = h3.inner_text().strip().lower()
            if section_title not in WANTED_SECTIONS:
                continue

            if section_title == "items":
                sub_sections = box.locator("div.m-3i8gv9").all()
                for sub in sub_sections:
                    h4 = sub.locator("h4").first
                    if not h4.count(): continue
                    sub_title = h4.inner_text().strip()
                    ids = extract_item_ids(sub)
                    if ids:
                        build_data[sub_title] = ids
            else:
                ids = extract_item_ids(box)
                if ids:
                    build_data[section_title.title()] = ids

        browser.close()

    if build_data:
        set_to_cache(key, build_data)  
        return build_data
    else:
        return {}  
    
def extract_item_ids(element):
    """Pomocná funkce na vytažení ID z obrázků v daném elementu"""
    ids = []
    imgs = element.locator('img[src*="game-items"]').all()
    for img in imgs:
        src = img.get_attribute("src")
        match = re.search(r"/game-items/(\d+)\.png", src)
        if match:
            ids.append(match.group(1))
    return ids

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

        self.setFixedSize(800, 530)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        
        main_layout = QHBoxLayout(self)

        redside = QVBoxLayout()
        blueside = QVBoxLayout()
        players = data["allPlayers"]

        # vytvoř pool s 8 vlákny
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(fetch_player_data, p) for p in players]
            results = [f.result() for f in futures]

        local_player = data.get("activePlayer", {}).get("summonerName", None)
        active_data = next((p for p in results if p["summname"] == local_player), None)
        active_lane = active_data["lane"]
        active_champ = rename_champs(active_data["champ"])

        self.executor = ThreadPoolExecutor(max_workers=2)

        def make_item_layout(items):
            vbox = QVBoxLayout()
            vbox.setSpacing(4)
            vbox.setContentsMargins(0,0,0,10) 
            row_layout = QHBoxLayout()
            row_layout.setSpacing(6)
            row_layout.setAlignment(Qt.AlignLeft)
            vbox.addLayout(row_layout)
            
            for i, item_id in enumerate(items):
                if i > 0 and i % 3 == 0: 
                    row_layout = QHBoxLayout()
                    row_layout.setSpacing(6)
                    row_layout.setAlignment(Qt.AlignLeft)
                    vbox.addLayout(row_layout)

                pix_path = resource_path(f"items_icons/{item_id}.png")
                pix = QPixmap(pix_path)
                if pix.isNull(): continue

                pix = pix.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl = QLabel()
                lbl.setPixmap(pix)
                lbl.setObjectName("ItemIcon") 
                lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                row_layout.addWidget(lbl)
            return vbox

        try:
            for player_data in results:
                if not player_data: continue

                p_team = player_data["team"]
                champ_name = rename_champs(player_data["champ"])
                summonername = player_data["summname"]
                rank_name = player_data["rank"]

                icon_path = (resource_path(f"icons/{champ_name}.png"))
                pixlbl = QLabel()
                pix = QPixmap(icon_path)
                pix = pix.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                pix = standardize_icon(pix, 80)
                pixlbl.setPixmap(pix)

                ranklbl = QLabel()
                rank_icon_file = check_what_rank(rank_name) if rank_name else "unranked.png"
                rank_path = resource_path(f"ranky/{rank_icon_file}")
                pixrank = QPixmap(rank_path)
                if not pixrank.isNull():
                    pixrank = pixrank.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    ranklbl.setPixmap(pixrank)
                else:
                    print(f"Chybí ikona ranku: {rank_path}")
                
                summonernamelbl = QLabel(summonername, self)
                summonernamelbl.setFixedWidth(150)
                summonernamelbl.setObjectName("summname")
                summonernamelbl.setAlignment(Qt.AlignCenter)
                
                info = QVBoxLayout()
                info.addWidget(summonernamelbl)
                info.addWidget(ranklbl)
                info.setAlignment(Qt.AlignCenter)

                player_row_widget = QWidget() 
                player_row_widget.setObjectName("playerrow")
                player_row = QHBoxLayout(player_row_widget)

                if p_team == "CHAOS":
                    player_row.addLayout(info)
                    player_row.addWidget(pixlbl)
                    redside.addWidget(player_row_widget)
                else:
                    player_row.addWidget(pixlbl)
                    player_row.addLayout(info)
                    blueside.addWidget(player_row_widget)
        except Exception as e: print(f"Error: {e}")

        redside.addStretch() 
        blueside.addStretch()

        separator = QLabel(); separator.setFixedWidth(2); separator.setStyleSheet("background-color: #3A3F4B;")
        separator2 = QLabel(); separator2.setFixedWidth(2); separator2.setStyleSheet("background-color: #3A3F4B;")

        
        build = search_build(active_champ, active_lane)
        guide_layout = QVBoxLayout()
        guide_layout.setAlignment(Qt.AlignTop)

        title_lbl = QLabel(f"Build for {active_champ.capitalize()}")
        title_lbl.setObjectName("guideTitle")
        guide_layout.addWidget(title_lbl)

        if isinstance(build, dict):
            for section, items in build.items():
                section_lbl = QLabel(section.upper())
                section_lbl.setObjectName("buildSection")
                guide_layout.addWidget(section_lbl)

                item_container_layout = make_item_layout(items) 
                w = QWidget()
                w.setLayout(item_container_layout)
                guide_layout.addWidget(w)
        
        guide_layout.addStretch() 

        left_panel_widget = QWidget()
        left_panel_widget.setLayout(guide_layout)

        main_layout.addWidget(left_panel_widget, 2)
        main_layout.addLayout(blueside, 1)
        main_layout.addWidget(separator)
        main_layout.addWidget(separator2)
        main_layout.addLayout(redside, 1)

        self.setLayout(main_layout)

    
