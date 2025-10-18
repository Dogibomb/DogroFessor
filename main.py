from api_key import API_KEY
from clash import clash_info
from user import get_summoners_level, get_champions_info_by_puuid_without_input, get_puuid, get_icon, check_what_rank, get_real_ranks, calculate_winrate
from freechamps import get_champions_info, get_free_champions
from match_history import convert_item_ids, get_user_normal_match_history, get_user_ranked_match_history, convert_match_ids, get_user_match_history
from config import *
from load_summoner import load_summoner_layout
import sys                
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox, QComboBox, QScrollArea, QSizePolicy, QFrame, QMenu
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QDateTime
from PyQt5.QtWidgets import QDialog, QShortcut
from PyQt5.QtGui import QPixmap, QIcon, QMovie, QKeySequence
from urllib.request import urlopen
from database import send_message, load_messages, supabase_client
from organization import *
from overlay import Overlay
import keyboard
import threading

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

class MainWindow(QWidget):
    def __init__(self, main_account=None):
        super().__init__()
        self.setWindowTitle('DogroFessor')
        
        
        self.setMinimumSize(1500, 800)

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
        btn_profile.clicked.connect(lambda: self.profile(main_account))

        btn_free_champions = QPushButton("Free champs")
        btn_free_champions.setFixedWidth(150)
        btn_free_champions.setGraphicsEffect(make_shadow())
        

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

        chat_button = QPushButton("→")
        chat_button.setObjectName("chatButton")
        chat_button.setGraphicsEffect(make_shadow())
        chat_button.clicked.connect(lambda: self.toggle_chat_panel(chat_button))
        

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
        top_bar.addWidget(btn_exit)
        top_bar.addStretch()
        top_bar.addWidget(chat_button)
        top_bar.setContentsMargins(0,0,40,0)
        
        self.right_column = QVBoxLayout()
        



        self.middle_widget = QWidget()
        self.middle_widget_layout = QVBoxLayout(self.middle_widget)
        self.middle_widget_layout.setContentsMargins(0,0,0,0)
        self.middle_widget_layout.setSpacing(8)
        self.middle_widget.setMaximumSize(600, 700)

        
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

        self.chat_panel = QFrame()
        self.chat_panel.setObjectName("chatPanel")



        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setObjectName("chatScrollArea")

        self.chat_scroll_content = QWidget()
        self.chat_scroll_layout = QVBoxLayout(self.chat_scroll_content)
        self.chat_scroll_layout.setAlignment(Qt.AlignTop)
        self.chat_scroll_area.setWidget(self.chat_scroll_content)

        self.chat_panel_layout = QVBoxLayout(self.chat_panel)
        self.chat_panel_layout.addWidget(QLabel("🌍 World Chat", alignment=Qt.AlignCenter))
        self.chat_panel_layout.addWidget(self.chat_scroll_area)
        self.chat_line = QLineEdit()
        self.chat_line.setPlaceholderText("Type Anything...")
        self.chat_line.returnPressed.connect(lambda: self.send_message(main_account_for_chat))
        self.chat_panel_layout.addWidget(self.chat_line)
        
        

        
        self.center_layout = QHBoxLayout()
        self.center_layout.addLayout(self.right_column, stretch=1)
        self.center_layout.addWidget(self.middle_widget, stretch=2)
        self.center_layout.addLayout(self.left_column, stretch=1)
        
        self.center_layout.addWidget(self.chat_panel, stretch=1)

        self.center_layout.setAlignment(Qt.AlignTop)

        self.loading_lbl = QLabel()
        self.loading_lbl.setVisible(False)
        self.loading_lbl.setAlignment(Qt.AlignCenter)
        

        icon = QMovie(resource_path("ikony/loading.gif"))
        self.loading_lbl.setMovie(icon)
        self.loading_icon = icon

        self.loading_lbl.setParent(self.middle_widget)
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

        

        self.chat_panel.setMinimumWidth(0)
        self.chat_panel.setMaximumWidth(0)
        
        self.chat_animation = QPropertyAnimation(self.chat_panel, b"maximumWidth")
        self.chat_open = False


        if main_account:
            try:
                if "#" in main_account:
                    name, tag = main_account.split("#", 1)
                    puuid = get_puuid(name, tag)
                    if puuid:
                        self.summ_name = main_account
                        main_account_for_chat = main_account
                        load_summoner_layout(self, puuid)
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Failed to load main account: {e}")


        self.overlay_window = None
        threading.Thread(target=self.hotkey, daemon=True).start()

    
    def hotkey(self):
        keyboard.add_hotkey("ctrl+y", lambda: self.toggle_overlay())
        keyboard.wait()

    def toggle_overlay(self):
        QTimer.singleShot(0, self._toggle_overlay_ui)

    def _toggle_overlay_ui(self):
        if self.overlay_window and self.overlay_window.isVisible():
            self.overlay_window.close()
            self.overlay_window = None
        else:
            self.overlay_window = Overlay()
            self.overlay_window.show()


    def send_message(self, account):
        chat_text = self.chat_line.text().strip()
        if not chat_text:
            return

        send_message(account, chat_text)

       
        self.chat_line.clear()

    def load_chat_history(self):
        try:
            messages = load_messages(limit=50)  

            
            for i in reversed(range(self.chat_panel_layout.count())):
                widget = self.chat_panel_layout.itemAt(i).widget()
                if widget and widget not in [self.chat_lbl, self.chat_line]:
                    widget.deleteLater()

            
            for msg in messages:
                self.display_message(msg["username"], msg["message"])

        except Exception as e:
            print("Error while loading chat:", e)

    def display_message(self, main_account_for_chat, message):
        msg_label = QLabel(f"<span style=\"font-weight: bold; color: #A78BFA; padding: 2px;\">{main_account_for_chat}</span> {QDateTime.currentDateTime().toString('hh:mm')} <br>{message}")
        msg_label.setWordWrap(True)
        msg_label.setObjectName("chatMessage")
        msg_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        msg_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.chat_scroll_layout.addWidget(msg_label)

        scroll_bar = self.chat_scroll_area.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def toggle_chat_panel(self, chat_button):

        self.chat_refresher = QTimer()
        self.chat_refresher.timeout.connect(self.load_chat_history)
        self.chat_refresher.start(500)

        current_width = self.chat_panel.width()

        if self.chat_open:
            self.chat_animation.setStartValue(current_width)
            self.chat_animation.setEndValue(0)
            chat_button.setText("→")
        else:
            self.chat_panel.setMinimumWidth(0)
            self.chat_panel.setMaximumWidth(300)
            self.chat_animation.setStartValue(current_width)
            self.chat_animation.setEndValue(300)
            chat_button.setText("←")

        self.chat_animation.start()
        self.chat_open = not self.chat_open

    

    def load_chat_history(self):
        try:
            # pokud ještě nemáme last_message_id, nastavíme 0 (začátek)
            if not hasattr(self, "last_message_id"):
                self.last_message_id = 0

            
            messages = load_messages(limit=10)

            messages = messages[::-1]  # reverzní pořadí, aby nejnovější byly na konci

            for msg in messages:
                # pokud zpráva je novější než poslední zobrazená, zobraz ji
                if msg["id"] > self.last_message_id:
                    self.display_message(msg["username"], msg["message"])
                    self.last_message_id = msg["id"]

        except Exception as e:
            print("❌ Error loading chat:", e)

    def match_load_finished(self, data):
        
        self.loading_icon.stop()
        self.loading_lbl.setVisible(False)


        load_summoner_layout(self, get_puuid(data["summoner_name"], data["summoner_tag"]))

    def set_region(self, region):
        self.selected_region = region

    def profile(self, main_account):
        if "#" not in main_account:
            QMessageBox.warning(self, "Warning", "Invalid main account format")
            return

        name, tag = main_account.split("#", 1)
        self.summ_name = main_account  
        puuid = get_puuid(name, tag)
        load_summoner_layout(self, puuid)

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