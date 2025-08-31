from PyQt6.QtWidgets import QApplication

from src import Prueba

class BysRot():
    def __init__(self):
        self.app = QApplication([])
        self.prueba = Prueba()
        self.app.exec()