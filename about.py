from PySide6.QtWidgets import QDialog, QLabel, QApplication
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class AboutWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_UI(self):
        self.setFixedSize(650, 330)
        self.setWindowTitle("About Me")
        self.setStyleSheet("""
            QDialog {
                font-family: Tahoma;
                font-size: 20px;
                background-color: white;
            }
            QLabel {
                background: transparent;
            }
        """)

        # Background image
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, 650, 330)
        self.background.setPixmap(QPixmap("assets/aboutme_wallpaper.jpg"))
        self.background.setScaledContents(True)

        # Name
        self.label1 = QLabel("Name: Joel Malich", self)
        self.label1.setGeometry(20, 10, 300, 30)
        self.label1.setStyleSheet("font-size: 22px; color: black; font-weight: bold;")

        # Email
        self.image1 = QLabel(self)
        self.image1.setPixmap(QPixmap("assets/email.png"))
        self.image1.setGeometry(20, 50, 30, 30)
        self.label2 = QLabel("joel.malich@s.afeka.ac.il", self)
        self.label2.setGeometry(60, 50, 400, 30)
        self.label2.setStyleSheet("color: #0044cc; text-decoration: underline;")

        # LinkedIn
        self.image2 = QLabel(self)
        self.image2.setPixmap(QPixmap("assets/linkedin.png"))
        self.image2.setGeometry(20, 90, 30, 30)
        self.label3 = QLabel('<a href="https://www.linkedin.com/in/joel-malich-b04a65202/">Joel Malich</a>', self)
        self.label3.setGeometry(60, 90, 400, 30)
        self.label3.setOpenExternalLinks(True)
        self.label3.setStyleSheet("color: #006699; font-size: 20px;")

        # Profile Picture or Related Image
        self.image3 = QLabel(self)
        self.image3.setPixmap(QPixmap("assets/snowwall.webp"))
        self.image3.setGeometry(320, 10, 300, 300)
        self.image3.setScaledContents(True)

        # University Logo
        self.image4 = QLabel(self)
        self.image4.setPixmap(QPixmap("assets/afeka.jpg"))
        self.image4.setGeometry(40, 190, 220, 100)
        self.image4.setScaledContents(True)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

if __name__ == "__main__":
    app = QApplication([])
    window = AboutWindow()
    window.exec()
