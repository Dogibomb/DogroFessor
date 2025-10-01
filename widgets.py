from imports import *

class InfoLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("summonerInfoTab")
        self.setAlignment(Qt.AlignCenter)
        self.setFixedWidth(500)
        self.setFixedHeight(37)

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