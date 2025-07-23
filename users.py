import csv
import os
import sys
import ast
from PySide6.QtWidgets import (
    QWidget, QLabel, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QApplication, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette


class PlayerHistoryViewer(QWidget):
    def __init__(self, csv_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Player History Viewer")
        self.setFixedSize(600, 500)
        self.csv_path = csv_path
        self.data = {}
        self.players = []

        self.setStyleSheet("""
            QWidget {
                background-color: #002B28;
                color: white;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 24px;
                font-weight: bold;
            }
            QComboBox {
                background-color: #004D40;
                color: white;
                font-size: 18px;
                padding: 5px;
                border: 1px solid #00695C;
                border-radius: 4px;
                min-width: 200px;
            }
            QPushButton {
                background-color: #6C757D;
                color: white;
                font-size: 18px;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QTableWidget {
                background-color: #004D40;
                color: white;
                font-size: 16px;
                gridline-color: #CCCCCC;
                border: 1px solid #666;
            }
            QHeaderView::section {
                background-color: #00695C;
                color: white;
                font-size: 16px;
            }
        """)

        # Title
        self.title_label = QLabel("Player History Viewer", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setGeometry(0, 10, self.width(), 40)

        # Player selection label
        self.select_label = QLabel("Select player:", self)
        self.select_label.setGeometry(30, 60, 130, 30)
        self.select_label.adjustSize()

        # Combo box
        self.combo = QComboBox(self)
        self.combo.setEditable(True)
        self.combo.setGeometry(200, 60, 180, 30)

        # Show history button
        self.show_button = QPushButton("Show History", self)
        self.show_button.setGeometry(430, 57, 130, 30)
        self.show_button.clicked.connect(self.show_history)
        self.show_button.adjustSize()

        # Table
        self.table = QTableWidget(self)
        self.table.setGeometry(25, 110, 550, 320)

        # Close button
        self.close_button = QPushButton("Close", self)
        self.close_button.setGeometry((self.width() - 120) // 2, 445, 120, 35)
        self.close_button.clicked.connect(self.close)

        self.load_csv()

    def load_csv(self):
        if not os.path.exists(self.csv_path):
            QMessageBox.critical(self, "Error", f"CSV file not found: {self.csv_path}")
            return

        try:
            with open(self.csv_path, newline='', encoding='utf-8') as f:
                reader = list(csv.reader(f))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read CSV file:\n{e}")
            return

        if not reader or len(reader) < 2:
            QMessageBox.information(self, "Info", "CSV file is empty or does not have enough data.")
            return

        self.players = [cell.strip() for cell in reader[0][1:] if cell.strip()]
        row_players = [row[0].strip() for row in reader[1:] if row[0].strip()]

        self.data = {p: {} for p in self.players}

        for r_idx, row in enumerate(reader[1:], start=1):
            row_player = row[0].strip()
            if row_player == "":
                continue
            for c_idx, cell in enumerate(row[1:], start=1):
                col_player = reader[0][c_idx].strip()
                cell = cell.strip()
                if cell:
                    try:
                        scores = ast.literal_eval(cell)
                        if isinstance(scores, list) and len(scores) == 2:
                            wins, losses = scores
                            if row_player in self.players and col_player in self.players:
                                self.data[row_player][col_player] = [wins, losses]
                    except Exception:
                        pass

        self.combo.clear()
        self.combo.addItems(self.players)

    def show_history(self):
        player = self.combo.currentText().strip()
        if player not in self.players:
            QMessageBox.warning(self, "Player Not Found", f"Player '{player}' not found in the CSV.")
            return

        opponents = [p for p in self.players if p != player]
        results = []

        for opponent in opponents:
            wins = losses = 0
            if player in self.data and opponent in self.data[player]:
                w, l = self.data[player][opponent]
                wins += w
                losses += l
            if opponent in self.data and player in self.data[opponent]:
                w, l = self.data[opponent][player]
                wins += l
                losses += w
            total = wins + losses
            win_rate = (wins / total * 100) if total > 0 else None
            results.append((opponent, wins, losses, total, win_rate))

        results.sort(key=lambda x: x[3], reverse=True)

        self.table.clear()
        self.table.setColumnCount(5)
        self.table.setRowCount(len(results))
        self.table.setHorizontalHeaderLabels(["Opponent", "Wins", "Losses", "Matches", "Win Rate (%)"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        for row, (opponent, wins, losses, total, win_rate) in enumerate(results):
            values = [
                opponent,
                str(wins),
                str(losses),
                str(total),
                "N/A" if win_rate is None else f"{win_rate:.1f}%"
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
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

    viewer = PlayerHistoryViewer("scoreboard.csv")
    viewer.show()
    sys.exit(app.exec())
