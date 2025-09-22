from api_key import API_KEY
from clash import clash_info
from user import get_User_info_by_puuid, get_summoners_level, print_user_info, get_champions_info_by_puuid_without_input, get_puuid, get_icon
from freechamps import get_champions_info, get_free_champions
from match_history import get_user_normal_match_history, get_user_ranked_match_history, convert_match_ids

import sys                
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QGridLayout, QSplitter, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QPainterPath

class InfoLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("summonerInfoTab")
        # self.setAlignment(Qt.AlignCenter)
        self.setFixedWidth(500)

def round_pixmap(pixmap):
    size = min(pixmap.width(), pixmap.height())
    rounded = QPixmap(size, size)
    rounded.fill(Qt.transparent)

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)
    
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)  # vytvoří kruh
    painter.setClipPath(path)
    
    # Nakreslí originální pixmapu do kruhu
    painter.drawPixmap(0, 0, size, size, pixmap)
    painter.end()
    
    return rounded        

def clash_info():
    pass
def match_history():
    pass
def free_champions():
    pass
def convert_puuid():
    pass

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DogroFessor')
        
        self.setFixedSize(1400, 800)

        self.setStyleSheet("""
            QWidget {
                background-color: #20232A;
                color: white;
                font-size: 18px;
            }

            QPushButton {
                background-color: #A78BFA;
                color: white;
                font-size: 20px;
                border-radius: 6px;
                padding: 6px 12px;
            }

            QPushButton:hover {
                background-color: #8B5CF6;
            }
            
            QPushButton:pressed{
                background-color: #7C3AED
            }

            QPushButton#exitButton {
                background-color: #8B5CF6;
                border-radius: 4px;
                width: 30px;
            }

            QLineEdit {
                background-color: #2C313C;
                border: 1px solid #A78BFA;
                color: white;
                font-size: 20px;
                padding: 6px;
                border-radius: 4px;
            }
            InfoLabel{
                background-color: #3A4556;
                color: white;
                font-size: 20px;
                padding: 6px;
                border-radius: 4px;   
            }
            iconLabel{
                border: 1px solid black;
                border-radius: 200px;
           }
            #topBar{
                background-color: #2C313C; 
                
            }
            #logo{
            background-color: #2C313C;
            margin: 0px;
            }
            #funcKeys{
                font-size: 20px;
            }          
        """)

        top_bar_widget = QWidget()
        top_bar_widget.setObjectName("topBar")
        top_bar = QHBoxLayout(top_bar_widget)
        top_bar.setContentsMargins(10, 10, 10, 10)
        top_bar_widget.setFixedHeight(70)
        
        logo = QLabel(top_bar_widget)
        pixmap = QPixmap("logo.png")
        pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setObjectName("logo")
        logo.setFixedSize(pixmap.size())
        logo.setContentsMargins(0, 0, 0, 0)
        logo.move(40, -5)

        
        

        btn_profile = QPushButton("Profil")
        btn_profile.setFixedWidth(150)

        btn_free_champions = QPushButton("Free champs")
        btn_free_champions.setFixedWidth(150)

        btn_convert_puuid = QPushButton("Convert Puuid")
        btn_convert_puuid.setFixedWidth(150)

        btn_clash_info = QPushButton("Clash Info")
        btn_clash_info.setFixedWidth(150)

        btn_exit = QPushButton("X")
        btn_exit.setFixedWidth(50)
        btn_exit.setFixedHeight(30)
        btn_exit.setObjectName("funcKeys")
        btn_exit.clicked.connect(self.close)

        btn_minimized = QPushButton("–")
        btn_minimized.setFixedWidth(50)
        btn_minimized.setFixedHeight(30)
        btn_minimized.setObjectName("funcKeys")
        btn_minimized.clicked.connect(self.showMinimized)

        btn_maximaze = QPushButton("▭")
        btn_maximaze.setFixedWidth(50)
        btn_maximaze.setFixedHeight(30)
        btn_maximaze.setObjectName("funcKeys")
        btn_maximaze.clicked.connect(self.toggleMaximaze)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("e.g Dogbomb#luv")
        self.search_box.setFixedWidth(200)
        self.search_box.setContentsMargins(0,0,10,0)
        self.search_box.returnPressed.connect(self.summoner_info)

        
        # top_bar.addWidget(logo)
        top_bar.addStretch()
        top_bar.addStretch()
        top_bar.addWidget(btn_profile)
        top_bar.addWidget(btn_free_champions)
        top_bar.addWidget(btn_convert_puuid)
        top_bar.addWidget(btn_clash_info)
        top_bar.addStretch()
        top_bar.addWidget(self.search_box)
       
        top_bar.addWidget(btn_minimized)
        top_bar.addWidget(btn_maximaze)
        top_bar.addWidget(btn_exit)

        


        self.center_layout = QHBoxLayout()

        



    
        
        main_layout = QVBoxLayout()
        
        main_layout.addWidget(top_bar_widget)
        main_layout.addStretch()
        main_layout.addLayout(self.center_layout)
        main_layout.addStretch()
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(main_layout)



    def summoner_info(self):
        
        text = self.search_box.text().strip()

        if "#" not in text:
            QMessageBox.warning(self, "Warning", "You have to enter valid tag in format Name#Tag")
            return

        name, tag = text.split("#", 1)

        puuid = get_puuid(name, tag)
        if puuid is None:
            return

        summoner_name, summoner_tag =get_champions_info_by_puuid_without_input(puuid)
        summoners_icon, summoners_level, summoners_rank = get_summoners_level(puuid)
        real_flex_rank, real_solo_duo_rank, summoners_icon, summoners_level, puuid = print_user_info(summoners_icon, summoners_level, puuid, summoners_rank)

        pixmap = get_icon(summoners_icon)
        
        if pixmap:
            pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pixmap = round_pixmap(pixmap)
            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            icon_label.setObjectName("iconLabel")
            self.center_layout.addWidget(icon_label)
        self.center_layout.addWidget(InfoLabel(f"{summoner_name}#{summoner_tag} / Level: {summoners_level}"))
        self.center_layout.addWidget(InfoLabel(f"Flex rank: {real_flex_rank}"))
        self.center_layout.addWidget(InfoLabel(f"Solo/Duo rank: {real_solo_duo_rank}"))
        

    def toggleMaximaze(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
    


        





app = QApplication(sys.argv)
icon = QIcon("logo.png")
app.setWindowIcon(icon)
window = MainWindow()
window.setWindowFlag(Qt.FramelessWindowHint)
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