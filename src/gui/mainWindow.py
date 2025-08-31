from PyQt6 import uic
from PyQt6.QtWidgets import QMessageBox

class MainWindow():
    def __init__(self):
        self.mainWindow = uic.loadUi('src/gui/mainWindow.ui')
        self.mainWindow.show()
