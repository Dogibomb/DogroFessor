from api_key import API_KEY
from clash import clash_info
from user import get_User_info_by_puuid, get_summoners_level, get_champions_info_by_puuid_without_input, get_puuid, get_icon, check_what_rank, get_real_ranks, calculate_winrate
from freechamps import get_champions_info, get_free_champions
from match_history import get_user_normal_match_history, get_user_ranked_match_history, convert_match_ids

import sys                
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QGridLayout, QSplitter, QMessageBox, QComboBox, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap, QIcon, QColor
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QPainterPath

class InfoLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("summonerInfoTab")
        self.setAlignment(Qt.AlignCenter)
        self.setFixedWidth(470)
        self.setFixedHeight(33)
        
def make_shadow():
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)       # jak moc je rozmazaný
    shadow.setXOffset(2)           # posun X
    shadow.setYOffset(2)           # posun Y
    shadow.setColor(QColor(0, 0, 0, 180))  # barva stínu
    return shadow

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
    
def standardize_icon(pixmap, size=300):
    canvas = QPixmap(size, size)
    canvas.fill(Qt.transparent)  # průhledné pozadí

    scaled = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    painter = QPainter(canvas)
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    painter.drawPixmap(x, y, scaled)
    painter.end()

    return canvas


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
        
        self.setFixedSize(1500, 800)

        self.dragPos = None

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
                background-color: #7C3AED;
            }

            QPushButton#exitButton {
                background-color: #8B5CF6;
                border-radius: 4px;
                width: 30px;
            }

            QLineEdit {
                margin-left: 10px;
                background-color: #2C313C;
                border: 1px solid #A78BFA;
                color: white;
                font-size: 20px;
                padding: 6px;
                border-radius: 4px;
            }
            InfoLabel{
                background-color: #2C313C;
                color: white;
                font-size: 20px;
                padding: 6px;
                border-radius: 4px;   
            }
            #iconLabel{
                background-color: transparent;
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
            #RegionBox{
                background-color: #2C313C;
                color: white;
                font-size: 16px;
                padding: 6px;
                border: 1px solid #A78BFA;
                border-radius: 2px;       
            }
            #RegionBox:hover {
                border: 1px solid #8B5CF6;
            }
            #RegionBox::drop-down {
                image: url(feature.png);
                border-left: 1px solid #A78BFA;
                width: 25px;
                background-color: #2C313C;
            }
            #RegionBox QAbstractItemView {
                color: white;
                selection-background-color: #8B5CF6;
                selection-color: white;
                border: 1px solid #A78BFA;
            }      
        """)

        top_bar_widget = QWidget()
        top_bar_widget.setObjectName("topBar")
        top_bar_widget.setFixedHeight(70)
        top_bar = QHBoxLayout(top_bar_widget)
        top_bar.setSpacing(8)
        top_bar.setContentsMargins(0, 0, 0, 0)
        
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
        btn_profile.setGraphicsEffect(make_shadow())

        btn_free_champions = QPushButton("Free champs")
        btn_free_champions.setFixedWidth(150)
        btn_free_champions.setGraphicsEffect(make_shadow())

        btn_convert_puuid = QPushButton("Convert Puuid")
        btn_convert_puuid.setFixedWidth(150)
        btn_convert_puuid.setGraphicsEffect(make_shadow())

        btn_clash_info = QPushButton("Clash Info")
        btn_clash_info.setFixedWidth(150)
        btn_clash_info.setGraphicsEffect(make_shadow())

        btn_exit = QPushButton("X")
        btn_exit.setFixedWidth(50)
        btn_exit.setFixedHeight(30)
        btn_exit.setObjectName("funcKeys")
        btn_exit.clicked.connect(self.close)
        btn_exit.setGraphicsEffect(make_shadow())

        btn_minimized = QPushButton("–")
        btn_minimized.setFixedWidth(50)
        btn_minimized.setFixedHeight(30)
        btn_minimized.setObjectName("funcKeys")
        btn_minimized.clicked.connect(self.showMinimized)
        btn_minimized.setGraphicsEffect(make_shadow())

        btn_maximaze = QPushButton("▭")
        btn_maximaze.setFixedWidth(50)
        btn_maximaze.setFixedHeight(30)
        btn_maximaze.setObjectName("funcKeys")
        btn_maximaze.clicked.connect(self.toggleMaximaze)
        btn_maximaze.setGraphicsEffect(make_shadow())

        self.region_box = QComboBox()
        
        self.region_box.setObjectName("RegionBox")
        self.region_box.addItems([
            "EUNE", "EUW", "KR", "NA", "LAN", "LAS", "OCE", "BR", "TR", "RU", "JP"
        ])
        self.selected_region = "EUNE"
        self.region_box.currentTextChanged.connect(self.set_region)

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
        top_bar.addWidget(self.region_box)
        top_bar.addWidget(self.search_box)
        top_bar.addWidget(btn_minimized)
        top_bar.addWidget(btn_maximaze)
        top_bar.addWidget(btn_exit)
        top_bar.setContentsMargins(0,0,10,0)
        
        self.right_column = QVBoxLayout()
        

        self.middle_column = QVBoxLayout()
        self.middle_column.setAlignment(Qt.AlignTop)
        

        self.left_column = QVBoxLayout()
        


        self.center_layout = QHBoxLayout()
        self.center_layout.addLayout(self.right_column, stretch=1)
        self.center_layout.addLayout(self.middle_column, stretch=1)
        self.center_layout.addLayout(self.left_column, stretch=1)
        self.center_layout.setAlignment(Qt.AlignTop)
        # self.center_layout.setContentsMargins(12, 12, 12, 12)
        # self.center_layout.setSpacing(40)

        main_layout = QVBoxLayout()
        
        main_layout.addWidget(top_bar_widget)
        
        main_layout.addLayout(self.center_layout)
        main_layout.addStretch()
        main_layout.setContentsMargins(0, 0, 0, 0)
        # main_layout.setSpacing(0)

        self.setLayout(main_layout)



    def set_region(self, region):
            self.selected_region = region

    def summoner_info(self):
        
        text = self.search_box.text().strip()

        if "#" not in text:
            QMessageBox.warning(self, "Warning", "You have to enter valid tag in format Name#Tag")
            return

        name, tag = text.split("#", 1)

        puuid = get_puuid(name, tag)
        if puuid is None:
            return

        summoner_name, summoner_tag = get_champions_info_by_puuid_without_input(puuid)
        summoners_icon, summoners_level, summoners_rank = get_summoners_level(puuid, self.selected_region)
        real_flex_rank, real_solo_duo_rank = get_real_ranks(summoners_rank)

        winrate = calculate_winrate(summoners_rank)

        self.left_column.addWidget(InfoLabel(f"Solo/Duo rank: {real_solo_duo_rank} / Winrate: {winrate[0]}%"), alignment=Qt.AlignTop | Qt.AlignLeft)

        pixmap = get_icon(summoners_icon)
        
        

        if pixmap:
            pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pixmap = round_pixmap(pixmap)
            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            icon_label.setObjectName("iconLabel")
            self.middle_column.addWidget(icon_label, alignment=Qt.AlignCenter)
        text_label = InfoLabel(f"{summoner_name}#{summoner_tag} / Level: {summoners_level}")
       

        info_widget = QWidget()
        info_row = QHBoxLayout()
        info_widget.setLayout(info_row)
        
        info_row.addWidget(text_label)
        info_row.addWidget(icon_label)


        self.middle_column.addWidget(info_widget)

        

        self.right_column.addWidget(InfoLabel(f"Flex rank: {real_flex_rank} / Winrate: {winrate[1]}%"), alignment=Qt.AlignTop | Qt.AlignRight)
        
        self.middle_column.setContentsMargins(0,0,0,0)
        self.right_column.setContentsMargins(0,12,0,0)
        self.left_column.setContentsMargins(0,12,0,0)

        rankIconsolo = check_what_rank(real_solo_duo_rank)
        rankIconflex = check_what_rank(real_flex_rank)

        logosolo = QLabel()
        pixmapsolo = QPixmap(f"ranky/{rankIconsolo}")
        pixmapsolo = pixmapsolo.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmapsolo = standardize_icon(pixmapsolo, 300)
        logosolo.setPixmap(pixmapsolo)
        logosolo.setObjectName("logoRank")
        logosolo.setAlignment(Qt.AlignCenter)

        self.left_column.addWidget(logosolo)

        logoflex = QLabel()
        pixmapflex = QPixmap(f"ranky/{rankIconflex}")
        pixmapflex = pixmapflex.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmapflex = standardize_icon(pixmapflex, 300)
        logoflex.setPixmap(pixmapflex)
        logoflex.setObjectName("logoRank")
        logoflex.setAlignment(Qt.AlignCenter)
        self.right_column.addWidget(logoflex)



    def toggleMaximaze(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragPos is not None:
            self.move(event.globalPos() - self.dragPos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = None

    
    


        





app = QApplication(sys.argv)
icon = QIcon("logo.png")
app.setWindowIcon(icon)
window = MainWindow()
window.setWindowFlag(Qt.FramelessWindowHint)
window.show()
sys.exit(app.exec_())