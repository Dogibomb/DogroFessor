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

def search_build(active_champ):
    try:
        key = f"build_{active_champ.lower()}"
        cached_item = get_from_cache(key)
        if cached_item:
            return cached_item
        
        active_champ = active_champ.capitalize()
        url = f"https://probuilds.net/champions/details/{active_champ}"
        headers = {
            "User-Agent":(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return f"⚠️ Failed to fetch data for {active_champ} (HTTP {res.status_code})."
        
        soup = BeautifulSoup(res.text, "html.parser")

        item_imgs = soup.select(".aggregate-container .items .item img")
        if not item_imgs:
             return f"⚠️ No items found for {active_champ}."

        item_ids = []
        for img in item_imgs:
            src = img.get("src", "")
            match = re.search(r"/item/(\d+)\.webp", src)
            if match:
                print(item_ids)
                item_ids.append(match.group(1))

        if not item_ids:
            return f"⚠️ Could not parse item IDs for {active_champ}."

        
        build = f"items for {active_champ.title()}:\n" + ", ".join(item_ids)
        
        set_to_cache(key, build)

        return build
    except Exception as e:
        return f"Build failed to load: {e}"

def gpt_asnwer(active_champ, active_lane, opponent, latest_patch):
    """
    Fetches meta build info (via CommunityDragon)
    + adds AI-generated coaching guide via OpenAI.
    """
    client = OpenAI(api_key=API_KEY_OPENAI)
    
    # ---- Build the AI prompt ----
    prompt = f"""
        You are an **elite League of Legends coach**. Create a concise, actionable **lane-specific guide** for the following:

        Champion: {active_champ}
        Opponent: {opponent or "unknown"}
        Lane: {active_lane}
        Patch: {latest_patch}

        Include these sections clearly:
        1. Skill Order
        2. Power Spikes
        3. Matchup Notes
        4. Counterplay Tips

        Rules:
        - Max 250 words.
        - No JSON or bullet lists without context.
        - Use short, natural sentences.
        - Give real matchup insights (cooldowns, spikes, trading tips).

        Example Style:
        "At level 3, use your Q-E combo to punish short trades. Hold W for disengage if the jungler is nearby."

        Now produce the guide.
        """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional League of Legends coach with deep meta knowledge."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=600,
        )

        ai_text = response.choices[0].message.content.strip()

        # Combine both build info + AI text
        final_output = f"{ai_text}"
        return final_output

    except Exception as e:
        # If OpenAI fails, return only build info
        return f"\n\n⚠️ AI guide generation failed: {e}"

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

        self.setFixedSize(1300, 700)
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

        self.executor = ThreadPoolExecutor(max_workers=2)

        guidelbl = QLabel("Loading your guide ...", self)
        guidelbl.setFixedHeight(700)
        guidelbl.setFixedWidth(650)
        guidelbl.setObjectName("guide")
        guidelbl.setAlignment(Qt.AlignCenter)
        guidelbl.setWordWrap(True)

        build_text = search_build(active_champ)
        item_ids = re.findall(r"\d+", build_text)

        def make_item_layout(items):
            vbox = QVBoxLayout()
            vbox.setSpacing(0)
            vbox.setContentsMargins(0,0,0,0)
            row_layout = None
            for i, item_id in enumerate(items):
                if i % 4 == 0:
                    row_layout = QHBoxLayout()
                    row_layout.setSpacing(4)
                    vbox.addLayout(row_layout)
                pix = QPixmap(resource_path(f"items_icons/{item_id}.png"))
                if pix.isNull():
                    continue  # skip if image missing
                pix = pix.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl = QLabel()
                lbl.setPixmap(pix)
                lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                row_layout.addWidget(lbl)
            return vbox

        

        def guide():
            if matchup_key in responses_cache:
                return responses_cache[matchup_key]
            try:
            
                response_text = gpt_asnwer(active_champ, active_lane, opponent, latest_patch)
                responses_cache[matchup_key] = response_text
                return response_text
            except Exception as e:
                import traceback
                traceback.print_exc()  
                return f"Error: {str(e)}"
        
        def on_done(fut):
            response_text = fut.result()
            QMetaObject.invokeMethod(
                guidelbl,
                "setText",
                Qt.QueuedConnection,
                Q_ARG(str, response_text)
            )
        
        future = self.executor.submit(guide)
        future.add_done_callback(on_done)

        
        try:
            for player_data in results:
                if not player_data:
                    continue
                
                

                team = player_data["team"]
                champ_name = rename_champs(player_data["champ"])
                lane = player_data["lane"]
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

        redside.setContentsMargins(40, 10, 20, 10)
        blueside.setContentsMargins(20, 10, 40, 10)

        main_layout.setContentsMargins(0,0,0,0)
        

        separator = QLabel()
        separator.setFixedWidth(2)
        separator.setStyleSheet("background-color: #3A3F4B; border-radius: 1px;")

        separator2 = QLabel()
        separator2.setFixedWidth(2)
        separator2.setStyleSheet("background-color: #3A3F4B; border-radius: 1px;")

        title_lbl = QLabel(f"optimal build for {active_champ.lower()}")
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setObjectName("guideTitle")

        item_layout = make_item_layout(item_ids)
        item_container = QWidget()
        item_container.setLayout(item_layout)
        item_container.setFixedHeight(80)

        guide_layout = QVBoxLayout()
        guide_layout.setAlignment(Qt.AlignTop)
        guide_layout.addWidget(title_lbl)
        guide_layout.addWidget(item_container, alignment=Qt.AlignCenter)

        guide_container = QWidget()
        guide_container.setFixedWidth(650)
        guide_container.setLayout(guide_layout)

        main_layout.addWidget(guide_container, alignment=Qt.AlignTop)
        main_layout.addLayout(blueside)
        main_layout.addWidget(separator)
        # main_layout.addWidget(guide_container, alignment=Qt.AlignCenter)
        main_layout.addWidget(separator2)
        main_layout.addLayout(redside)

        self.setLayout(main_layout)

    
