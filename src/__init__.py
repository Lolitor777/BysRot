from PyQt6 import uic
from PyQt6.QtWidgets import QMessageBox

class Prueba():
    def __init__(self):
        self.prueba = uic.loadUi('src/gui/ui.ui')
        self.prueba.show()



