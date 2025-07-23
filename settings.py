from PySide6.QtWidgets import (
    QRadioButton, QButtonGroup, QWidget, QDialog,
    QLabel, QPushButton, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
import sys
import os


class PointsToWinSelector(QWidget):
    def __init__(self, selected_value: int, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 40)
        self.points_to_win_group = QButtonGroup(self)

        spacing = 10
        btn_width = 50
        btn_height = 30
        start_x = 0

        for i, val in enumerate([3, 5, 7, 9, 11]):
            btn = QRadioButton(str(val), self)
            btn.setGeometry(start_x + i * (btn_width + spacing), 0, btn_width, btn_height)
            btn.setStyleSheet("font-size: 18px; color: white;")
            if val == selected_value:
                btn.setChecked(True)
            self.points_to_win_group.addButton(btn)

    def get_selected_points(self) -> int:
        for btn in self.points_to_win_group.buttons():
            if btn.isChecked():
                return int(btn.text())
        return 5


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: white;
            }
            QRadioButton {
                font-size: 18px;
                color: white;
            }
            QPushButton {
                font-size: 18px;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton#saveButton {
                background-color: #28A745;
                color: white;
            }
            QPushButton#closeButton {
                background-color: #6C757D;
                color: white;
            }
        """)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#00332E"))
        self.setPalette(palette)

        self.init_ui()

    def init_ui(self):
        # Container
        self.container = QWidget(self)
        self.container.setGeometry(50, 50, 400, 300)
        self.container.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            border-radius: 15px;
        """)

        # Points to Win
        self.points_label = QLabel("Points to Win:", self.container)
        self.points_label.setGeometry(20, 20, 200, 30)

        if not os.path.exists("settings.txt"):
            with open("settings.txt", "w") as f:
                f.write("1,5")

        current_points = int(open("settings.txt").read().split(",")[1].strip())
        self.points_selector = PointsToWinSelector(current_points, self.container)
        self.points_selector.setGeometry(20, 60, 360, 40)

        # Audio
        self.audio_label = QLabel("Audio:", self.container)
        self.audio_label.setGeometry(20, 120, 200, 30)

        audio_state = open("settings.txt").read().split(",")[0].strip() == "1"
        self.audio_on = QRadioButton("On", self.container)
        self.audio_off = QRadioButton("Off", self.container)

        self.audio_on.setGeometry(120, 120, 60, 30)
        self.audio_off.setGeometry(190, 120, 60, 30)

        self.audio_on.setChecked(audio_state)
        self.audio_off.setChecked(not audio_state)

        self.audio_group = QButtonGroup(self)
        self.audio_group.addButton(self.audio_on)
        self.audio_group.addButton(self.audio_off)

        # Save and Close buttons
        self.save_btn = QPushButton("Save", self.container)
        self.save_btn.setObjectName("saveButton")
        self.save_btn.setGeometry(80, 230, 100, 40)

        self.close_btn = QPushButton("Close", self.container)
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setGeometry(220, 230, 100, 40)

        self.save_btn.clicked.connect(self.save_settings)
        self.close_btn.clicked.connect(self.close)

    def save_settings(self):
        audio_value = 1 if self.audio_on.isChecked() else 0
        points_value = self.points_selector.get_selected_points()
        with open("settings.txt", "w") as f:
            f.write(f"{audio_value},{points_value}")
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor("#00332E"))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor("#004D40"))
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor("#007BFF"))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    app.setPalette(dark_palette)

    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())
