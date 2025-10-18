from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QProxyStyle, QStyle
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import QPixmap, QColor, QPainterPath, QPainter



class ToolTipStyle(QProxyStyle):
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.SH_ToolTip_WakeUpDelay:
            return 1  
        return super().styleHint(hint, option, widget, returnData)

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
