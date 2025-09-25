from api_key import API_KEY
from clash import clash_info
from user import get_summoners_level, get_champions_info_by_puuid_without_input, get_puuid, get_icon, check_what_rank, get_real_ranks, calculate_winrate
from freechamps import get_champions_info, get_free_champions
from match_history import get_user_normal_match_history, get_user_ranked_match_history, convert_match_ids

import sys                
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QGridLayout, QSplitter, QMessageBox, QComboBox, QGraphicsDropShadowEffect, QScrollArea, QSizePolicy, QFrame
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap, QIcon, QColor, QPainterPath, QPainter, QBrush
from urllib.request import urlopen
from io import BytesIO

class InfoLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("summonerInfoTab")
        self.setAlignment(Qt.AlignCenter)
        self.setFixedWidth(470)
        self.setFixedHeight(37)

def get_pixmap_from_url(url):
    try:
        data = urlopen(url).read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        return pixmap
    except Exception as e:
        print("Failed to load pixmap:", e)
        return QPixmap("placeholder.png")  # fallback


class MatchWidget(QWidget):
    def __init__(self, team1_icons, team2_icons, result_text="", icon_size=40):
        super().__init__()
        self.setObjectName("matchWidget")
        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(6, 6, 6, 6)

        # levý tým (5 ikon)
        left = QWidget()
        left_layout = QHBoxLayout()
        left_layout.setSpacing(6)
        left_layout.setContentsMargins(0,0,0,0)
        left.setLayout(left_layout)

        for path in team1_icons:
            lbl = QLabel()
            pix = get_pixmap_from_url(path) 
            pix = pix.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl.setPixmap(pix)
            lbl.setFixedSize(icon_size, icon_size)
            left_layout.addWidget(lbl)

        # výsledek uprostřed
        mid = QLabel(result_text)
        mid.setFixedWidth(160)
        mid.setAlignment(Qt.AlignCenter)
        mid.setObjectName("matchResultLabel")

        # pravý tým (5 ikon)
        right = QWidget()
        right_layout = QHBoxLayout()
        right_layout.setSpacing(6)
        right_layout.setContentsMargins(0,0,0,0)
        right.setLayout(right_layout)

        for path in team2_icons:
            lbl = QLabel()
            pix = get_pixmap_from_url(path)
            pix = pix.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl.setPixmap(pix)
            lbl.setFixedSize(icon_size, icon_size)
            right_layout.addWidget(lbl)

        layout.addWidget(left, 1)
        layout.addWidget(mid, 0)
        layout.addWidget(right, 1)
        self.setLayout(layout)

        # čára pod zápasem (opcionalně)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_v = QVBoxLayout()
        main_v.setContentsMargins(0,0,0,0)
        main_v.addLayout(layout)
        main_v.addWidget(line)
        self.setLayout(main_v)


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

def clearLayout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            clearLayout(item.layout())

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DogroFessor')
        
        self.setFixedSize(1500, 800)

        self.dragPos = None

        with open("styles.qss", "r") as f:
            self.setStyleSheet(f.read())

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
        btn_free_champions.clicked.connect(self.free_champs)

        btn_convert_puuid = QPushButton("Find Group")
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

    def free_champs(self):
        pass
        # get_free_champions()

    # vypisuje summoners info to vyhledevani basicly
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

        clearLayout(self.left_column)
        clearLayout(self.middle_column)
        clearLayout(self.right_column)

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

        match_ids = get_user_ranked_match_history(summoner_name, summoner_tag)
        matches_data = convert_match_ids(match_ids)
        
        matches_layout = QVBoxLayout()

        

        for m in matches_data:
            
            team1_champs = [f"http://ddragon.leagueoflegends.com/cdn/15.19.1/img/champion/{p['champion']}.png" for p in m["team1"]]
            
            team2_champs = [f"http://ddragon.leagueoflegends.com/cdn/15.19.1/img/champion/{p['champion']}.png" for p in m["team2"]]
            result_text = f"{m['duration']} min"

            match_widget = MatchWidget(team1_champs, team2_champs, result_text)
            self.middle_column.addWidget(match_widget)

        self.right_column.addWidget(InfoLabel(f"Flex rank: {real_flex_rank} / Winrate: {winrate[1]}%"), alignment=Qt.AlignTop | Qt.AlignRight)
        
        self.middle_column.setContentsMargins(0,0,0,0)
        self.right_column.setContentsMargins(0,10,0,0)
        self.left_column.setContentsMargins(0,10,0,0)

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