from PyQt6.QtWidgets import QApplication

from src.gui.mainWindow import MainWindow


class BysRot():
    def __init__(self):
        self.app = QApplication([])
        self.mainWindow = MainWindow()
        self.app.exec()