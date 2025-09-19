from api_key import API_KEY
from clash import clash_info
from user import get_User_info_by_puuid, get_summoners_level, print_user_info, get_champions_info_by_puuid_without_input, get_puuid
from freechamps import get_champions_info, get_free_champions
from match_history import get_user_normal_match_history, get_user_ranked_match_history, convert_match_ids

import sys                
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap

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
window.setWindowTitle('DogroFessor')
window.setGeometry(400, 150, 1200, 700)
# window.setWindowIcon("logo.jpg")

window.setStyleSheet("background-color: #2D3848;")



top_bar = QHBoxLayout()
logo = QLabel()
pixmap = QPixmap("logo.jpeg")
pixmap = pixmap.scaled(200,50)
logo.setPixmap(pixmap)

btn_profile = QPushButton("Profil")

btn_free_champions = QPushButton("Free champs")
btn_free_champions.setFixedWidth(150)

search_box = QLineEdit()
search_box.setPlaceholderText("Search ...")
search_box.setFixedWidth(200)

top_bar.addWidget(logo)
top_bar.addStretch()
top_bar.addWidget(btn_profile)
top_bar.addWidget(btn_free_champions)
top_bar.addStretch()
top_bar.addWidget(search_box)



center_layout = QVBoxLayout()
welcome_label = QLabel('Welcome to DogroFessor', window)
btn_match_history = QPushButton("Match history")
btn_match_history.setFixedWidth(200)

center_layout.addWidget(welcome_label, alignment=Qt.AlignCenter)
center_layout.addWidget(btn_match_history, alignment=Qt.AlignCenter)


bottom_bar = QHBoxLayout()
btn_convert_puuid = QPushButton("Convert Puuid")
btn_convert_puuid.setFixedWidth(150)
btn_exit = QPushButton("Exit")
btn_exit.setFixedWidth(50)
btn_clash_info = QPushButton("Clash Info")
btn_clash_info.setFixedWidth(120)

bottom_bar.addStretch()
bottom_bar.addWidget(btn_convert_puuid)
bottom_bar.addWidget(btn_exit)
bottom_bar.addWidget(btn_clash_info)
bottom_bar.addStretch()



main_layout = QVBoxLayout()
main_layout.addLayout(top_bar)
main_layout.addStretch()
main_layout.addLayout(center_layout)
main_layout.addStretch()
main_layout.addLayout(bottom_bar)


# search_box.clicked.connect(summoner_info)
btn_match_history.clicked.connect(match_history)
btn_clash_info.clicked.connect(clash_info)
btn_free_champions.clicked.connect(free_champions)
btn_convert_puuid.clicked.connect(convert_puuid)
btn_exit.clicked.connect(exit)



btn_match_history.setStyleSheet("background-color: #3A4556; color: white; font-size: 20px;")
btn_clash_info.setStyleSheet("background-color: #3A4556; color: white; font-size: 20px;")
btn_free_champions.setStyleSheet("background-color: #3A4556; color: white; font-size: 20px;")
btn_convert_puuid.setStyleSheet("background-color: #3A4556; color: white; font-size: 20px;")
btn_exit.setStyleSheet("background-color: #3A4556; color: white; font-size: 20px;")
btn_profile.setStyleSheet("background-color: #3A4556; color: white; font-size: 20px;")

search_box.setStyleSheet("background-color: #3A4556; color: white; font-size: 20px;")
welcome_label.setStyleSheet("color: white; font-size: 60px; ")



window.setLayout(main_layout)
window.show()
sys.exit(app.exec_())



    # if user_input == "1":
    #     puuid = get_puuid()
    #     summoners_name, summoners_level, summoners_rank = get_summoners_level(puuid)
    #     print_user_info(summoners_name, summoners_level, puuid, summoners_rank)
        
    # elif user_input == "2":
    #     clash_info()
    # elif user_input == "3":
    #     print("For Normal matches press 1")
    #     print("For Ranked matches press 2")
    #     user_input2 = input("Enter your choice: ")
    #     if user_input2 == "1":
    #         convert_match_ids(get_user_normal_match_history())
    #     elif user_input2 == "2":
    #         convert_match_ids(get_user_ranked_match_history())
    # elif user_input == "4":
    #     get_free_champions()
    # elif user_input == "5":
    #     get_User_info_by_puuid()
    # elif user_input == "x":
    #     break
    # else:
    #     print("Wrong input")