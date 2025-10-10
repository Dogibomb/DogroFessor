from imports import resource_path, clearLayout, round_pixmap, standardize_icon
from widgets import InfoLabel, MatchWidget
from user import get_puuid, get_champions_info_by_puuid_without_input, get_summoners_level, get_real_ranks, calculate_winrate, get_icon, check_what_rank
from match_history import get_user_match_history, convert_match_ids, convert_item_ids
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

def load_summoner_layout(self, puuid):
    summoner_name, summoner_tag = get_champions_info_by_puuid_without_input(puuid)
    summoners_icon, summoners_level, summoners_rank = get_summoners_level(puuid, self.selected_region)
    real_flex_rank, real_solo_duo_rank, lp_flex, lp_solo, wins_flex, wins_solo, losses_flex, losses_solo = get_real_ranks(summoners_rank)

    winrate = calculate_winrate(summoners_rank)

    clearLayout(self.matches_layout)
    clearLayout(self.left_column)
    clearLayout(self.info_layout)      
    clearLayout(self.right_column)
    clearLayout(self.matches_layout)

    

    pixmap = get_icon(summoners_icon)
    
    # vytvoření textu a ikony
    text_label = InfoLabel(f"{summoner_name}#{summoner_tag} / Level: {summoners_level}")

    icon_label = QLabel()
    if pixmap:
        pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap = round_pixmap(pixmap)
        icon_label.setPixmap(pixmap)
        icon_label.setObjectName("iconLabel")

    
    info_widget = QWidget()
    info_row = QHBoxLayout()
    info_widget.setLayout(info_row)
    info_row.addWidget(text_label)
    info_row.addWidget(icon_label)

    
    self.info_layout.addWidget(info_widget)

    

    match_ids = get_user_match_history(summoner_name, summoner_tag)
    matches_data = convert_match_ids(match_ids, summoner_name)        



    for m in matches_data:
        
        team1_champs = [
            {"icon": resource_path(f"icons/{p['champion']}.png"), "name": p["name"]}
            for p in m["team1"]]
                            
        team2_champs = [
            {"icon": resource_path(f"icons/{p['champion']}.png"), "name": p["name"]}
            for p in m["team2"]]
        my_item_ids = m['items']
        
        duration = f"{m['duration']} min"
        
        kda = f"{m["kda"]}"

        item_names = convert_item_ids(my_item_ids)

        match_widget = MatchWidget(team1_champs, team2_champs, duration, self.summ_name, kda, my_item_ids, item_names)


        self.matches_layout.addWidget(match_widget)


    #soloque     
    solo_container = QHBoxLayout()
    solo_container.setAlignment(Qt.AlignTop)
    header = QLabel("Solo/Duo")
    header.setObjectName("rankHeader")
    header.setAlignment(Qt.AlignCenter)
    header.setFixedHeight(30)

    header.setContentsMargins(0,0,0,0)
    self.right_column.addWidget(header)

    rankIconsolo = check_what_rank(real_solo_duo_rank)
    winrate_solo = winrate[0]

    logosolo = QLabel()
    pixmapsolo = QPixmap(resource_path(f"ranky/{rankIconsolo}"))
    pixmapsolo = pixmapsolo.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    pixmapsolo = standardize_icon(pixmapsolo, 150)
    logosolo.setPixmap(pixmapsolo)
    logosolo.setObjectName("logoRank")
    logosolo.setAlignment(Qt.AlignCenter)

    

    solo_info_layout = QVBoxLayout()

    solo_info_layout.addWidget(QLabel(f"<span style='font-weight: bold;'>{real_solo_duo_rank}</span>"))
    solo_info_layout.addWidget(QLabel(f"LP: {lp_solo}"))
    solo_info_layout.addWidget(QLabel(f"<span style='color: #00FF66;'>Wins: {wins_solo}</span>"))
    solo_info_layout.addWidget(QLabel(f"<span style='color: #FF3333;'>Losses: {losses_solo}</span>"))
    solo_info_layout.addWidget(QLabel(f"Winrate: {winrate_solo}%"))

    solo_container.addWidget(logosolo)
    solo_container.addLayout(solo_info_layout)

    self.right_column.addLayout(solo_container)

    
    #flex
    flex_container = QHBoxLayout()
    flex_container.setAlignment(Qt.AlignTop)
    flex_container.setContentsMargins(0,0,0,0)
    headerflex = QLabel("Flex")
    headerflex.setObjectName("rankHeader")
    headerflex.setAlignment(Qt.AlignCenter)
    headerflex.setFixedHeight(30)
    
    self.left_column.addWidget(headerflex)

    winrate_flex = winrate[1]
    rankIconflex = check_what_rank(real_flex_rank)

    logoflex = QLabel()
    pixmapflex = QPixmap(resource_path(f"ranky/{rankIconflex}"))
    pixmapflex = pixmapflex.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    pixmapflex = standardize_icon(pixmapflex, 150)
    logoflex.setPixmap(pixmapflex)
    logoflex.setObjectName("logoRank")
    logoflex.setAlignment(Qt.AlignCenter)

    

    flex_info_layout = QVBoxLayout()
    flex_container.setContentsMargins(0,0,0,0)
    flex_info_layout.addWidget(QLabel(f"<span style='font-weight: bold;'>{real_flex_rank}</span>"))
    flex_info_layout.addWidget(QLabel(f"LP: {lp_flex}"))
    flex_info_layout.addWidget(QLabel(f"<span style='color: #00FF66; '>Wins: {wins_flex}</span>"))
    flex_info_layout.addWidget(QLabel(f"<span style='color: #FF3333; '>Losses: {losses_flex}</span>"))
    flex_info_layout.addWidget(QLabel(f"Winrate: {winrate_flex}%"))
    
    flex_container.addWidget(logoflex)
    flex_container.addLayout(flex_info_layout)

    self.left_column.addLayout(flex_container)
    
    self.middle_widget_layout.setContentsMargins(0,0,0,0)
    self.right_column.setContentsMargins(0,10,0,0)
    self.left_column.setContentsMargins(0,10,0,0)
