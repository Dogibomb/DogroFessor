from api_key import API_KEY
from clash import clash_info
from user import get_User_info_by_puuid, get_summoners_level, print_user_info, get_champions_info_by_puuid_without_input, get_puuid
from freechamps import get_champions_info, get_free_champions
from match_history import get_user_normal_match_history, get_user_ranked_match_history, convert_match_ids

import sys                
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

class SummonerInfoDialog(QDialog):
    def __init__(self, summoners_icon, summoners_level, real_flex_rank, real_solo_duo_rank, puuid, summoner_name, summoner_tag):
        super().__init__()
        self.setWindowTitle("Summoner Info")
        self.setStyleSheet("background-color: black; color: white; font-size: 20px;")

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Summoners Name: {summoner_name}"))
        layout.addWidget(QLabel(f"Summoner Tag: {summoner_tag}"))
        layout.addWidget(QLabel(f"Summoners Icon: {summoners_icon}"))
        layout.addWidget(QLabel(f"Level: {summoners_level}"))
        layout.addWidget(QLabel(f"Flex rank: {real_flex_rank}"))
        layout.addWidget(QLabel(f"Solo/Duo rank: {real_solo_duo_rank}"))
        layout.addWidget(QLabel(f"PUUID: <span style='color: gray'>{puuid}</span>"))

        self.setLayout(layout)


def summoner_info():
    puuid = get_puuid()
    summoner_name, summoner_tag =get_champions_info_by_puuid_without_input(puuid)
    summoners_icon, summoners_level, summoners_rank = get_summoners_level(puuid)
    real_flex_rank, real_solo_duo_rank, summoners_icon, summoners_level, puuid = print_user_info(summoners_icon, summoners_level, puuid, summoners_rank)

    dialog = SummonerInfoDialog(summoners_icon, summoners_level, real_flex_rank, real_solo_duo_rank, puuid, summoner_name, summoner_tag)
    dialog.exec_()

def clash_info():
    pass
def match_history():
    pass
def free_champions():
    pass
def convert_puuid():
    pass
def exit():
    sys.exit()

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle('DogoPedia')
window.setGeometry(400, 150, 1200, 700)

layout = QVBoxLayout()

welcome_label = QLabel('Welcome to DogoPedia', window)
welcome_label.setWordWrap(True)
layout.addWidget(welcome_label)

# Create buttons
btn_summoner_info = QPushButton('Summoner Info', window)
btn_summoner_info.clicked.connect(summoner_info)
layout.addWidget(btn_summoner_info)

btn_match_history = QPushButton('Match History', window)
btn_match_history.clicked.connect(match_history)
layout.addWidget(btn_match_history)

btn_clash_info = QPushButton('Clash Info', window)
btn_clash_info.clicked.connect(clash_info)
layout.addWidget(btn_clash_info)

btn_free_champions = QPushButton('Free Champions', window)
btn_free_champions.clicked.connect(free_champions)
layout.addWidget(btn_free_champions)

btn_convert_puuid = QPushButton('Convert PUUID', window)
btn_convert_puuid.clicked.connect(convert_puuid)
layout.addWidget(btn_convert_puuid)

btn_exit = QPushButton('Exit', window)
btn_exit.clicked.connect(exit)
layout.addWidget(btn_exit)

window.setLayout(layout)
window.show()
sys.exit(app.exec_())



user_input = ''

while(True):
    
    print("\n-------------------------------")

    

    print("-------------------------------\n")

    user_input = input("Enter your choice: ")

    print("-------------------------------")

    if user_input == "1":
        puuid = get_puuid()
        summoners_name, summoners_level, summoners_rank = get_summoners_level(puuid)
        print_user_info(summoners_name, summoners_level, puuid, summoners_rank)
        
    elif user_input == "2":
        clash_info()
    elif user_input == "3":
        print("For Normal matches press 1")
        print("For Ranked matches press 2")
        user_input2 = input("Enter your choice: ")
        if user_input2 == "1":
            convert_match_ids(get_user_normal_match_history())
        elif user_input2 == "2":
            convert_match_ids(get_user_ranked_match_history())
    elif user_input == "4":
        get_free_champions()
    elif user_input == "5":
        get_User_info_by_puuid()
    elif user_input == "x":
        break
    else:
        print("Wrong input")