import os
import csv
import sys
from PySide6.QtWidgets import (
    QDialog, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QMessageBox, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette


def get_user_record(user_name: str, filename="scoreboard.csv") -> tuple[int, int]:
    if not os.path.exists(filename):
        return 0, 0

    with open(filename, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))

    if len(reader) < 2:
        return 0, 0

    headers = reader[0][1:]
    rows = {row[0]: row[1:] for row in reader[1:]}

    user = user_name.strip()
    if user not in headers and user not in rows:
        return 0, 0

    wins = losses = 0

    if user in rows:
        for cell in rows[user]:
            try:
                w, l = eval(cell)
                wins += w
                losses += l
            except:
                continue

    if user in headers:
        col_idx = headers.index(user)
        for row_data in rows.values():
            if len(row_data) > col_idx:
                try:
                    w, l = eval(row_data[col_idx])
                    wins += l
                    losses += w
                except:
                    continue

    return wins, losses


class HighScoresWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("High Scores")
        self.setFixedSize(600, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #002B28;
            }
            QLabel {
                color: white;
                font-size: 26px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #6C757D;
                color: white;
                font-size: 20px;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QTableWidget {
                background-color: #004D40;
                color: white;
                font-size: 18px;
                gridline-color: #CCCCCC;
                border: 1px solid #666;
            }
            QHeaderView::section {
                background-color: #00695C;
                color: white;
                font-size: 18px;
            }
        """)

        self.title = QLabel("High Scores", self)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setGeometry(0, 10, self.width(), 40)

        self.table = QTableWidget(self)
        self.table.setGeometry(25, 60, self.width() - 50, 360)

        self.close_btn = QPushButton("Close", self)
        self.close_btn.setGeometry((self.width() - 150) // 2, 440, 150, 40)
        self.close_btn.clicked.connect(self.close)

        self.load_scores()

    def load_scores(self):
        path = "scoreboard.csv"
        if not os.path.exists(path):
            QMessageBox.warning(self, "File Not Found", "scoreboard.csv was not found.")
            return

        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = list(csv.reader(f))
        except Exception as e:
            QMessageBox.critical(self, "Read Error", f"Failed to read file:\n{e}")
            return

        if len(reader) < 2:
            QMessageBox.information(self, "Empty Data", "No player records found.")
            return

        headers = reader[0][1:]
        row_names = [row[0] for row in reader[1:]]
        all_players = sorted(set(headers + row_names))

        self.table.setRowCount(len(all_players))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Player", "Wins", "Losses", "Win Rate (%)"])

        for row, name in enumerate(all_players):
            wins, losses = get_user_record(name, path)
            total = wins + losses
            winrate = f"{(wins / total * 100):.1f}" if total else "N/A"

            for col, val in enumerate([name, str(wins), str(losses), winrate]):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()


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

    window = HighScoresWindow()
    window.show()
    sys.exit(app.exec())
