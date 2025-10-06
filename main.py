from api_key import API_KEY
from clash import clash_info
from user import get_summoners_level, get_champions_info_by_puuid_without_input, get_puuid, get_icon, check_what_rank, get_real_ranks, calculate_winrate
from freechamps import get_champions_info, get_free_champions
from match_history import convert_item_ids, get_user_normal_match_history, get_user_ranked_match_history, convert_match_ids, get_user_match_history
from config import *
from load_summoner import load_summoner_layout
import sys                
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QGridLayout, QSplitter, QMessageBox, QComboBox, QGraphicsDropShadowEffect, QScrollArea, QSizePolicy, QFrame, QProxyStyle, QStyle, QInputDialog, QMenu
from PyQt5.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap, QIcon, QColor, QPainterPath, QPainter, QBrush, QMovie
from urllib.request import urlopen
from io import BytesIO

class LoadingIcon(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, name, tag, region):
        super().__init__()
        self.name = name
        self.tag = tag
        self.region = region
    
    def run(self):
        try:
            puuid = get_puuid(self.name, self.tag)
            if not puuid:
                raise Exception("Could not get puuid")

            summoner_name, summoner_tag = get_champions_info_by_puuid_without_input(puuid)
            summoners_icon, summoners_level, summoners_rank = get_summoners_level(puuid, self.region)
            real_flex_rank, real_solo_duo_rank, lp_flex, lp_solo, wins_flex, wins_solo, losses_flex, losses_solo = get_real_ranks(summoners_rank)
            winrate = calculate_winrate(summoners_rank)

            match_ids = get_user_match_history(summoner_name, summoner_tag)
            matches_data = convert_match_ids(match_ids, summoner_name)

            data = {
                "summoner_name": summoner_name,
                "summoner_tag": summoner_tag,
                "summoners_icon": summoners_icon,
                "summoners_level": summoners_level,
                "summoners_rank": summoners_rank,
                "real_flex_rank": real_flex_rank,
                "real_solo_duo_rank": real_solo_duo_rank,
                "lp_flex": lp_flex,
                "lp_solo": lp_solo,
                "wins_flex": wins_flex,
                "wins_solo": wins_solo,
                "losses_flex": losses_flex,
                "losses_solo": losses_solo,
                "winrate": winrate,
                "matches_data": matches_data
            }

            self.finished.emit(data)
        except Exception as e:
            self.error.emit(str(e))


class CustomInputDialog(QDialog):
    def __init__(self, title, label_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(350, 110)
        self.setObjectName("inputDialog")
        
        with open(resource_path("styles.qss"), "r") as f:
            self.setStyleSheet(f.read())

        layout = QVBoxLayout()
        self.label = QLabel(label_text)
        self.input = QLineEdit()
        self.button = QPushButton("OK")
        self.button.clicked.connect(self.accept)

        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def get_input(self):
        if self.exec_() == QDialog.Accepted:
            return self.input.text(), True
        else:
            return "", False

def get_mainAcc_Again():
    config = load_config()

    inputdialog = CustomInputDialog("Main Account", "Enter your main account (Name#Tag):")
    name, ok = inputdialog.get_input()

    if ok and name:
        config["mainAcc"] = name
        save_config(config)
        return name
    return None

def get_mainAcc():
    config = load_config()
    if "mainAcc" in config:
        return config["mainAcc"]

    inputdialog = CustomInputDialog("Main Account", "Enter your main account (Name#Tag):")
    name, ok = inputdialog.get_input()

    if ok and name:
        config["mainAcc"] = name
        save_config(config)
        return name
    return None

class InfoLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("summonerInfoTab")
        self.setAlignment(Qt.AlignCenter)
        self.setFixedWidth(500)
        self.setFixedHeight(37)

class ToolTipStyle(QProxyStyle):
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.SH_ToolTip_WakeUpDelay:
            return 1  
        return super().styleHint(hint, option, widget, returnData)

class MatchWidget(QWidget):
    def __init__(self, team1_icons, team2_icons, duration, name, kda, items, item_names):
        super().__init__()
        self.setObjectName("matchWidget")

        

        def make_team_layout(icons):
            vbox = QVBoxLayout()
            vbox.setSpacing(0)
            vbox.setContentsMargins(0,0,0,0)
            row_layout = None
            my_icon_champ = None
            for i, player in enumerate(icons):
                if i % 5 == 0:
                    row_layout = QHBoxLayout()
                    row_layout.setSpacing(0)
                    vbox.addLayout(row_layout)
                pix = QPixmap(resource_path(player["icon"]))
                pix = pix.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl = QLabel()
                lbl.setPixmap(pix)
                
               
                lbl.setToolTip(player["name"])
                lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                
                if player["name"].lower() == name.lower():
                    lbl.setStyleSheet("border: 2px solid limegreen; border-radius: 5px;")
                    my_icon_champ = player["icon"]
                
                row_layout.addWidget(lbl)
            return vbox, my_icon_champ
        
        def make_item_layout(items):
            vbox = QVBoxLayout()
            vbox.setSpacing(0)
            vbox.setContentsMargins(0,0,0,0)
            row_layout = None
            for i, item_name in enumerate(items):
                if i % 4 == 0:
                    row_layout = QHBoxLayout()
                    row_layout.setSpacing(0)
                    vbox.addLayout(row_layout)
                pix = QPixmap(resource_path(f"items_icons/{item_name}"))
                pix = pix.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl = QLabel()
                lbl.setPixmap(pix)
                lbl.setToolTip(item_names[i])
                lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                
                row_layout.addWidget(lbl)
            return vbox

        team1_layout, champ1_icon = make_team_layout(team1_icons)
        team2_layout, champ2_icon = make_team_layout(team2_icons)

        team_container_layout = QVBoxLayout()
        team_container_layout.setContentsMargins(0,0,0,0)
        team_container_layout.setSpacing(0)
        team_container_layout.addLayout(team1_layout)
        team_container_layout.addLayout(team2_layout)

        teams_container = QWidget()
        teams_container.setLayout(team_container_layout)

        champ_info = QVBoxLayout()
        champ_info.setAlignment(Qt.AlignCenter)

        my_icon_champ = champ1_icon or champ2_icon
        
        kda_stat = QLabel(kda) 

        if my_icon_champ:
            pix = QPixmap(my_icon_champ).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation) 
            champ_label = QLabel() 
            
            champ_label.setPixmap(pix) 
            champ_info.addWidget(champ_label, alignment=Qt.AlignCenter)

        duration = QLabel(f"Game Duration: {duration}")
        
        champ_widget = QWidget()
        champ_widget.setLayout(champ_info)

        left_layout = QVBoxLayout()
        left_layout.addWidget(teams_container, alignment=Qt.AlignLeft)
        
        middle_layout = QVBoxLayout()
        middle_layout.addWidget(duration, alignment=Qt.AlignCenter)
        middle_layout.addWidget(champ_widget, alignment=Qt.AlignCenter)
        champ_info.addWidget(kda_stat, alignment=Qt.AlignCenter)

        item_layout = make_item_layout(items)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(20,0,0,0)
        right_layout.addLayout(item_layout)

        left_middle_right = QHBoxLayout()
        left_middle_right.setContentsMargins(0,0,20,0)
        left_middle_right.setSpacing(0)
        left_middle_right.addLayout(left_layout)
        left_middle_right.addLayout(middle_layout)
        left_middle_right.addLayout(right_layout)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        main_layout.addLayout(left_middle_right)
        
        
        

        line = QFrame()
        line.setObjectName("Line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        
        main_layout.addWidget(line)
    
        self.setLayout(main_layout)

def resource_path(relative_path):
    import sys, os
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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
    def __init__(self, main_account=None):
        super().__init__()
        self.setWindowTitle('DogroFessor')
        
        self.setFixedSize(1500, 800)

        self.dragPos = None


        with open(resource_path("styles.qss"), "r") as f:
            self.setStyleSheet(f.read())
        

        top_bar_widget = QWidget()
        top_bar_widget.setObjectName("topBar")
        top_bar_widget.setFixedHeight(70)
        top_bar = QHBoxLayout(top_bar_widget)
        
        top_bar.setContentsMargins(0, 0, 0, 0)
        
        logo = QPushButton(top_bar_widget) 
        pixmap = QPixmap(resource_path("ikony/logo.png")) 
        pixmap = pixmap.scaled(150, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation) 
        logo.setIcon(QIcon(pixmap)) 
        logo.setObjectName("logo") 
        logo.setIconSize(pixmap.size())
        logo.setFixedSize(pixmap.size()) 
        logo.setContentsMargins(0, 0, 0, 0) 
        

        account_changer = QMenu(logo)
        change_account_action = account_changer.addAction("Change Main Account")
        

        change_account_action.triggered.connect(lambda: get_mainAcc_Again())

        logo.setMenu(account_changer)

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
        
        
        self.region_box.addItems([
            "EUNE", "EUW", "KR", "NA", "LAN", "LAS", "OCE", "BR", "TR", "RU", "JP"
        ])
        self.selected_region = "EUNE"
        self.region_box.currentTextChanged.connect(self.set_region)
        arrow_path = resource_path("ikony/arrow2.png").replace("\\", "/")
        self.region_box.setStyleSheet(f"""
        QComboBox {{
            background-color: #2C313C;
            color: white;
            font-size: 16px;
            padding: 6px;
            border: 1px solid #A78BFA;
            border-radius: 2px;
        }}

        QComboBox:hover {{
            border: 1px solid #8B5CF6;
        }}

        QComboBox::drop-down {{
            image: url("{arrow_path}");
            border-left: 1px solid #A78BFA;
            width: 18px;
            
            background-color: #2C313C;
        }}

        QComboBox QAbstractItemView {{
            color: white;
            selection-background-color: #8B5CF6;
            selection-color: white;
            border: 1px solid #A78BFA;
        }}
        """)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("e.g Dogbomb#luv")
        self.search_box.setFixedWidth(200)
        self.search_box.setContentsMargins(0,0,10,0)
        self.search_box.returnPressed.connect(self.summoner_info)

        top_bar.addStretch()
        top_bar.addWidget(logo)
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
        top_bar.setContentsMargins(0,0,40,0)
        
        self.right_column = QVBoxLayout()
        



        self.middle_widget = QWidget()
        self.middle_widget_layout = QVBoxLayout(self.middle_widget)
        self.middle_widget_layout.setContentsMargins(0,0,0,0)
        self.middle_widget_layout.setSpacing(8)
        self.middle_widget.setFixedSize(600, 700)

        
        self.info_holder = QWidget()
        self.info_layout = QVBoxLayout(self.info_holder)
        self.info_layout.setContentsMargins(0,0,0,0)
        self.info_layout.setSpacing(4)
        self.middle_widget_layout.addWidget(self.info_holder)

        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(630)
        
        self.scroll_content = QWidget()
        self.matches_layout = QVBoxLayout(self.scroll_content)
        self.matches_layout.setContentsMargins(0,0,5,0)
        self.matches_layout.setSpacing(6)
        self.matches_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        self.middle_widget_layout.addWidget(self.scroll_area)

        

        self.left_column = QVBoxLayout()
        
        
        self.center_layout = QHBoxLayout()
        self.center_layout.addLayout(self.right_column, stretch=1)
        self.center_layout.addWidget(self.middle_widget, stretch=2)
        self.center_layout.addLayout(self.left_column, stretch=1)
        self.center_layout.setAlignment(Qt.AlignTop)
        

        self.loading_lbl = QLabel()
        self.loading_lbl.setVisible(False)
        self.loading_lbl.setAlignment(Qt.AlignCenter)
        

        icon = QMovie(resource_path("ikony/loading.gif"))
        self.loading_lbl.setMovie(icon)
        self.loading_icon = icon

        self.loading_lbl.setParent(self.middle_widget)
        # self.loading_lbl.resize(100, 100)
        self.loading_lbl.move(
            (self.middle_widget.width() - self.loading_lbl.width()) // 2,
            (self.middle_widget.height() - self.loading_lbl.height()) // 2
        )
        self.loading_lbl.raise_()

        main_layout = QVBoxLayout()
        
        main_layout.addWidget(top_bar_widget)
        
        main_layout.addLayout(self.center_layout)
        main_layout.addStretch()
        main_layout.setContentsMargins(0, 0, 0, 0)
        # main_layout.setSpacing(0)

        self.setLayout(main_layout)

        if main_account:
            try:
                if "#" in main_account:
                    name, tag = main_account.split("#", 1)
                    puuid = get_puuid(name, tag)
                    if puuid:
                        self.summ_name = main_account
                        load_summoner_layout(self, name, tag, puuid)
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Failed to load main account: {e}")

    def match_load_finished(self, data):
        
        self.loading_icon.stop()
        self.loading_lbl.setVisible(False)

        
        load_summoner_layout(self, data["summoner_name"], data["summoner_tag"], get_puuid(data["summoner_name"], data["summoner_tag"]))

    def set_region(self, region):
        self.selected_region = region

    def free_champs(self):
        pass
        # get_free_champions()

    # vypisuje summoners info to vyhledevani basicly
    def summoner_info(self):
        
        clearLayout(self.left_column)
        clearLayout(self.info_layout)      
        clearLayout(self.right_column)
        clearLayout(self.matches_layout)

        text = self.search_box.text().strip()

        if "#" not in text:
            QMessageBox.warning(self, "Warning", "You have to enter valid tag in format Name#Tag")
            return

        self.summ_name = text

        name, tag = text.split("#", 1)

        self.loading_lbl.setVisible(True)
        self.loading_icon.start()
        
        self.loader_thread = LoadingIcon(name, tag, self.selected_region)
        self.loader_thread.finished.connect(self.match_load_finished)
        # self.loader_thread.error.connect(self.on_match_load_error)
        self.loader_thread.start()

        # summoner_name, summoner_tag = get_champions_info_by_puuid_without_input(puuid)
        # summoners_icon, summoners_level, summoners_rank = get_summoners_level(puuid, self.selected_region)
        # real_flex_rank, real_solo_duo_rank, lp_flex, lp_solo, wins_flex, wins_solo, losses_flex, losses_solo = get_real_ranks(summoners_rank)

        # winrate = calculate_winrate(summoners_rank)

        # clearLayout(self.left_column)
        # clearLayout(self.info_layout)      
        # clearLayout(self.right_column)
        # clearLayout(self.matches_layout)

        # match_ids = get_user_match_history(summoner_name, summoner_tag)
        # matches_data = convert_match_ids(match_ids, summoner_name)

        # pixmap = get_icon(summoners_icon)
        
        # vytvoření textu a ikony
        # text_label = InfoLabel(f"{summoner_name}#{summoner_tag} / Level: {summoners_level}")

        # icon_label = QLabel()
        # if pixmap:
        #     pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        #     pixmap = round_pixmap(pixmap)
        #     icon_label.setPixmap(pixmap)
        #     icon_label.setObjectName("iconLabel")

        
        # info_widget = QWidget()
        # info_row = QHBoxLayout()
        # info_widget.setLayout(info_row)
        # info_row.addWidget(text_label)
        # info_row.addWidget(icon_label)

        
        # self.info_layout.addWidget(info_widget)

        

        
        

        



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
app.setStyle(ToolTipStyle())
icon = QIcon(resource_path("logo.png"))
app.setWindowIcon(icon)

main_account = get_mainAcc()

window = MainWindow(main_account)
window.setWindowFlag(Qt.FramelessWindowHint)
window.show()



sys.exit(app.exec_())