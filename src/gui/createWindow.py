from PyQt6.QtWidgets import QDialog
from PyQt6 import uic


class CreateWindow(QDialog):
    def __init__(self):
        super().__init__()

        uic.loadUi('src/gui/createWindow.ui', self)

        
        self.buttonCreate.clicked.connect(self.accept)
        self.buttonCancel.clicked.connect(self.reject)
        


    def getData(self):
        
        return {
            'nombre': self.inputNameProduct.text().strip(),
            'codigo': self.inputCodeProduct.text().strip(),
            'peso': self.inputKg.text().strip(),
            'rotulos': self.inputNumRots.text().strip()
        }