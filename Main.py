import sys
import os
import csv
import subprocess
from Game import Game
from about import AboutWindow
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QRadioButton, QButtonGroup, QMessageBox
)
from PySide6.QtGui import QPixmap, QIcon, QColor, QPalette, QPainter, QPainterPath, QPen
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class OutlinedLabel(QLabel):
    def __init__(self, text="", parent=None, outline_color=Qt.black, outline_width=2):
        super().__init__(text, parent)
        self.outline_color = outline_color
        self.outline_width = outline_width

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        font = self.font()
        fm = self.fontMetrics()
        text = self.text()
        x = (self.width() - fm.horizontalAdvance(text)) / 2
        y = (self.height() + fm.ascent() - fm.descent()) / 2
        path.addText(x, y, font, text)
        pen = QPen(self.outline_color)
        pen.setWidth(self.outline_width)
        painter.setPen(pen)
        painter.drawPath(path)
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.drawText(self.rect(), Qt.AlignCenter, text)


class VideoPlayerWindow(QMainWindow):
    def __init__(self, video_path):
        super().__init__()
        self.setWindowTitle("Video Player")
        self.setGeometry(150, 150, 640, 480)

        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)

        video_widget = QVideoWidget()
        self.setCentralWidget(video_widget)
        self.media_player.setVideoOutput(video_widget)

        if os.path.exists(video_path):
            self.media_player.setSource(QUrl.fromLocalFile(video_path))
            self.media_player.play()
        else:
            QMessageBox.critical(self, "Error", "Video file not found.")


class BackgammonMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Backgammon")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("backgammon_icon.png"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.background_label = QLabel(self.central_widget)
        pixmap = QPixmap("assets/background.webp")
        if not pixmap.isNull():
            self.background_label.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            self.background_label.setScaledContents(True)
        else:
            self.background_label.setText("Background Image Not Found")
            self.background_label.setStyleSheet("color: red; font-size: 24px;")

        self.overlay_widget = QWidget(self.central_widget)
        self.overlay_widget.setAttribute(Qt.WA_StyledBackground, True)
        self.overlay_widget.setStyleSheet("background: transparent;")
        self.overlay_layout = QVBoxLayout(self.overlay_widget)
        self.overlay_layout.setAlignment(Qt.AlignCenter)

        self.show_main_menu()

    def resizeEvent(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.overlay_widget.setGeometry(0, 0, self.width(), self.height())

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
                item.layout().deleteLater()

    def _styled_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("font-size: 18px; color: white;")
        return label

    def show_main_menu(self):
        self.clear_layout(self.overlay_layout)

        header_label = OutlinedLabel("Backgammon", outline_color=Qt.black, outline_width=3)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 48px; color: white; font-weight: bold;")
        self.overlay_layout.addWidget(header_label)

        def create_button(text, color, callback):
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                background-color: {color};
                color: white;
                font-size: 24px;
                padding: 10px 20px;
                border-radius: 5px;
            """)
            btn.clicked.connect(callback)
            self.overlay_layout.addWidget(btn, alignment=Qt.AlignCenter)

        create_button("Play", "#007BFF", self.show_game_settings)
        create_button("User History", "#17A2B8", self.show_user_history)
        create_button("Watch Video", "#FFC107", self.open_video_window)
        create_button("Open .docx File", "#DC3545", self.open_docx_file)

        about_button = QPushButton("About")
        about_button.setStyleSheet("""
            background-color: #6F42C1;
            color: white;
            font-size: 24px;
            padding: 10px 20px;
            border-radius: 5px;
        """)
        about_button.clicked.connect(self.show_about_window)
        self.overlay_layout.addWidget(about_button, alignment=Qt.AlignCenter)

    def show_about_window(self):
        self.about_window = AboutWindow()
        self.about_window.exec()

    def open_video_window(self):
        video_path = "assets/Game_review.mp4"
        self.video_window = VideoPlayerWindow(video_path)
        self.video_window.show()

    def open_docx_file(self):
        docx_path = os.path.abspath("assets/game_description.docx")
        if not os.path.exists(docx_path):
            QMessageBox.critical(self, "Error", f"File not found: {docx_path}")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(docx_path)
            elif sys.platform.startswith("darwin"):
                subprocess.run(["open", docx_path])
            else:
                subprocess.run(["xdg-open", docx_path])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")

    def show_game_settings(self):
        self.clear_layout(self.overlay_layout)

        header = OutlinedLabel("Game Settings", outline_color=Qt.black, outline_width=3)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 32px; color: white; font-weight: bold;")

        container = QWidget()
        container.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            border-radius: 15px;
            padding: 20px;
        """)
        form_layout = QVBoxLayout(container)

        player_names_layout = QHBoxLayout()
        self.player1_input = QLineEdit()
        self.player1_input.setPlaceholderText("Player 1 Name")
        self.player1_input.setStyleSheet("font-size: 22px; padding: 5px;")
        self.player2_input = QLineEdit()
        self.player2_input.setPlaceholderText("Player 2 Name")
        self.player2_input.setStyleSheet("font-size: 22px; padding: 5px;")

        player_names_layout.addWidget(self._styled_label("Player 1:"))
        player_names_layout.addWidget(self.player1_input)
        player_names_layout.addWidget(self._styled_label("Player 2:"))
        player_names_layout.addWidget(self.player2_input)
        form_layout.addLayout(player_names_layout)

        form_layout.addWidget(self._styled_label("Points to Win:"))
        self.points_to_win_group = QButtonGroup(self)
        points_layout = QHBoxLayout()
        for val in [3, 5, 7, 9, 11]:
            btn = QRadioButton(str(val))
            btn.setStyleSheet("font-size: 18px; color: white;")
            if val == 5:
                btn.setChecked(True)
            self.points_to_win_group.addButton(btn)
            points_layout.addWidget(btn)
        form_layout.addLayout(points_layout)

        form_layout.addWidget(self._styled_label("Audio:"))
        self.audio_on = QRadioButton("On")
        self.audio_off = QRadioButton("Off")
        self.audio_on.setChecked(True)
        for btn in [self.audio_on, self.audio_off]:
            btn.setStyleSheet("font-size: 18px; color: white;")
        audio_layout = QHBoxLayout()
        audio_layout.addWidget(self.audio_off)
        audio_layout.addWidget(self.audio_on)
        form_layout.addLayout(audio_layout)

        button_layout = QHBoxLayout()
        start_button = QPushButton("Start Game")
        start_button.setStyleSheet("background-color: #28A745; color: white; font-size: 18px; padding: 10px 20px;")
        back_button = QPushButton("Back")
        back_button.setStyleSheet("background-color: #6C757D; color: white; font-size: 18px; padding: 10px 20px;")
        button_layout.addWidget(back_button)
        button_layout.addWidget(start_button)
        form_layout.addLayout(button_layout)

        self.overlay_layout.addWidget(header)
        self.overlay_layout.addStretch()
        self.overlay_layout.addWidget(container, alignment=Qt.AlignCenter)
        self.overlay_layout.addStretch()

        start_button.clicked.connect(self.start_game)
        back_button.clicked.connect(self.show_main_menu)

    def start_game(self):
        p1 = self.player1_input.text().strip()
        p2 = self.player2_input.text().strip()
        if not p1 or not p2:
            QMessageBox.warning(self, "Error", "Please enter names for both players.")
            return

        points = next(int(btn.text()) for btn in self.points_to_win_group.buttons() if btn.isChecked())
        audio = self.audio_on.isChecked()

        confirm = QMessageBox.question(
            self, "Confirm Settings",
            f"<b>Game Settings:</b><br>Player 1: {p1}<br>Player 2: {p2}<br>Points to Win: {points}<br>"
            f"Audio: {'Enabled' if audio else 'Disabled'}",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            player_names = (p1, p2)
            score = [0, 0]
            game_instance = Game(self, player_names, points, score)
            game_instance.run()

    def show_user_history(self):
        self.clear_layout(self.overlay_layout)

        header = OutlinedLabel("User History", outline_color=Qt.black, outline_width=3)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 32px; color: white; font-weight: bold;")

        container = QWidget()
        container.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            border-radius: 15px;
            padding: 20px;
        """)
        layout = QVBoxLayout(container)

        input_layout = QHBoxLayout()
        self.history_name1 = QLineEdit()
        self.history_name1.setPlaceholderText("Player 1 Name")
        self.history_name1.setStyleSheet("font-size: 20px; padding: 5px;")
        self.history_name2 = QLineEdit()
        self.history_name2.setPlaceholderText("Player 2 Name")
        self.history_name2.setStyleSheet("font-size: 20px; padding: 5px;")
        input_layout.addWidget(self.history_name1)
        input_layout.addWidget(self.history_name2)
        layout.addLayout(input_layout)

        self.score_result_label = QLabel("")
        self.score_result_label.setStyleSheet("font-size: 22px; color: white;")
        self.score_result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.score_result_label)

        btn_layout = QHBoxLayout()
        check_button = QPushButton("Check Score")
        check_button.setStyleSheet("background-color: #28A745; color: white; font-size: 18px; padding: 10px 20px;")
        check_button.clicked.connect(self.check_score_history)

        back_button = QPushButton("Back")
        back_button.setStyleSheet("background-color: #6C757D; color: white; font-size: 18px; padding: 10px 20px;")
        back_button.clicked.connect(self.show_main_menu)

        btn_layout.addWidget(back_button)
        btn_layout.addWidget(check_button)
        layout.addLayout(btn_layout)

        self.overlay_layout.addWidget(header)
        self.overlay_layout.addStretch()
        self.overlay_layout.addWidget(container, alignment=Qt.AlignCenter)
        self.overlay_layout.addStretch()

    def check_score_history(self):
        name1 = self.history_name1.text().strip()
        name2 = self.history_name2.text().strip()

        if not name1 or not name2:
            QMessageBox.warning(self, "Input Error", "Both names must be filled in.")
            return

        if name1.lower() == name2.lower():
            QMessageBox.warning(self, "Input Error", "Names must be different.")
            return

        csv_path = "scoreboard.csv"
        if not os.path.exists(csv_path):
            QMessageBox.warning(self, "File Error", "scoreboard.csv not found.")
            return

        try:
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                headers = rows[0][1:]
                data = {row[0]: row[1:] for row in rows[1:]}

                if name1 not in data or name2 not in headers:
                    QMessageBox.information(self, "Not Found", f"No score found for {name1} vs {name2}.")
                    self.score_result_label.setText("")
                    return

                index = headers.index(name2)
                score = data[name1][index]
                self.score_result_label.setText(f"<b>{name1}</b> vs <b>{name2}</b>: Score = <b>{score}</b>")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read score: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor("#00332E"))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor("#004D40"))
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor("#007BFF"))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    app.setPalette(dark_palette)

    window = BackgammonMenu()
    window.show()
    sys.exit(app.exec())