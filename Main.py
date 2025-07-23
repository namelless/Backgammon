import sys
import os
from Game import Game
from about import AboutWindow
from scores import HighScoresWindow
from settings import SettingsWindow
from users import PlayerHistoryViewer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QLabel, QLineEdit, QMessageBox
)
from PySide6.QtGui import QPixmap, QIcon, QColor, QPalette
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


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
        self.overlay_widget = QWidget(self.central_widget)
        self.overlay_widget.setAttribute(Qt.WA_StyledBackground, True)
        self.overlay_widget.setStyleSheet("background: transparent;")

        self.widgets = []
        self.current_screen = "main_menu"

        self.show_main_menu()

    def resizeEvent(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.overlay_widget.setGeometry(0, 0, self.width(), self.height())

        if self.current_screen == "main_menu":
            self.reposition_widgets()
        elif self.current_screen == "game_settings":
            self.reposition_game_settings()

    def clear_widgets(self):
        for w in self.widgets:
            w.setParent(None)
            w.deleteLater()
        self.widgets.clear()

    def add_widget(self, widget):
        self.widgets.append(widget)
        widget.setParent(self.overlay_widget)
        widget.show()

    def reposition_widgets(self):
        spacing = 60
        start_y = (self.height() - (len(self.widgets) * spacing)) // 2
        for i, widget in enumerate(self.widgets):
            widget.resize(300, 45)
            widget.move((self.width() - widget.width()) // 2, start_y + i * spacing)

    def reposition_game_settings(self):
        if not hasattr(self, "player1_input") or not hasattr(self, "player2_input"):
            return

        center_x = self.width() // 2

        for widget in self.widgets:
            if isinstance(widget, QLabel) and widget.text() == "Enter Player Names":
                widget.move(center_x - widget.width() // 2, 80)
            elif widget == self.player1_input:
                widget.move(center_x - 150, 160)
            elif widget == self.player2_input:
                widget.move(center_x - 150, 220)
            elif isinstance(widget, QPushButton):
                if widget.text() == "Start Game":
                    widget.move(center_x - 160, 300)
                elif widget.text() == "Back":
                    widget.move(center_x + 20, 300)

    def show_main_menu(self):
        self.current_screen = "main_menu"
        self.clear_widgets()

        header_label = QLabel("Backgammon", self.overlay_widget)
        header_label.setStyleSheet("font-size: 48px; color: white; font-weight: bold;")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.adjustSize()
        header_label.show()
        self.widgets.append(header_label)

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
            self.add_widget(btn)

        create_button("Play", "#007BFF", self.show_game_settings)
        create_button("User History", "#17A2B8", self.show_user_history)
        create_button("High Scores", "#28A745", self.show_high_scores)
        create_button("Settings", "#343A40", self.show_settings_window)
        create_button("Watch Video", "#FFC107", self.open_video_window)
        create_button("Open .docx File", "#DC3545", self.open_docx_file)
        create_button("About", "#6F42C1", self.show_about_window)

        self.reposition_widgets()

        pixmap = QPixmap("assets/background.webp")
        if not pixmap.isNull():
            self.background_label.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            self.background_label.setScaledContents(True)
        else:
            self.background_label.setText("Background Image Not Found")
            self.background_label.setStyleSheet("color: red; font-size: 24px;")

    def show_game_settings(self):
        self.clear_widgets()

        label = QLabel("Enter Player Names", self.overlay_widget)
        label.setStyleSheet("font-size: 32px; color: white; font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        label.resize(400, 50)
        self.widgets.append(label)

        self.player1_input = QLineEdit(self.overlay_widget)
        self.player1_input.setPlaceholderText("Player 1 Name")
        self.player1_input.setStyleSheet("font-size: 22px; padding: 5px;")
        self.player1_input.resize(300, 40)
        self.widgets.append(self.player1_input)

        self.player2_input = QLineEdit(self.overlay_widget)
        self.player2_input.setPlaceholderText("Player 2 Name")
        self.player2_input.setStyleSheet("font-size: 22px; padding: 5px;")
        self.player2_input.resize(300, 40)
        self.widgets.append(self.player2_input)

        start_btn = QPushButton("Start Game", self.overlay_widget)
        start_btn.setStyleSheet("background-color: #28A745; color: white; font-size: 18px; padding: 10px 20px;")
        start_btn.resize(140, 40)
        start_btn.clicked.connect(self.start_game)
        self.widgets.append(start_btn)

        back_btn = QPushButton("Back", self.overlay_widget)
        back_btn.setStyleSheet("background-color: #6C757D; color: white; font-size: 18px; padding: 10px 20px;")
        back_btn.resize(140, 40)
        back_btn.clicked.connect(self.show_main_menu)
        self.widgets.append(back_btn)

        self.current_screen = "game_settings"
        
        self.reposition_game_settings()
        for widget in self.widgets:
            widget.show()

    def start_game(self):
        p1 = self.player1_input.text().strip()
        p2 = self.player2_input.text().strip()
        if not p1 or not p2:
            QMessageBox.warning(self, "Error", "Please enter names for both players.")
            return
        if p1.lower() == p2.lower():
            QMessageBox.warning(self, "Error", "Player names must be different.")
            return

        audio, points = [int(x) for x in open("settings.txt").read().strip().split(",")]

        confirm = QMessageBox.question(
            self, "Confirm Settings",
            f"<b>Game Settings:</b><br>Player 1: {p1}<br>Player 2: {p2}<br>Points to Win: {points}<br>"
            f"Audio: {'Enabled' if audio else 'Disabled'}",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            game = Game(self, (p1, p2), points, [0, 0])
            game.audio_on = audio
            game.run()

    def show_user_history(self):
        self.player_history_window = PlayerHistoryViewer("scoreboard.csv")
        self.player_history_window.show()

    def show_high_scores(self):
        self.high_scores_window = HighScoresWindow()
        self.high_scores_window.show()

    def show_settings_window(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def show_about_window(self):
        self.about_window = AboutWindow()
        self.about_window.show()

    def open_video_window(self):
        self.video_window = VideoPlayerWindow("video")
        self.video_window.show()

    def open_docx_file(self):
        path = os.path.abspath("assets/game_description.docx")
        if not os.path.exists(path):
            QMessageBox.critical(self, "Error", f"File not found: {path}")
            return
        try:
            if sys.platform.startswith('win'):
                os.startfile(path)
            elif sys.platform.startswith('darwin'):
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")


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
