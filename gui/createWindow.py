from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtGui import QIntValidator
from PyQt6 import uic
from absoluteRouts import resource_path
 


class CreateWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path('gui/createWindow.ui'), self)
        
        self.buttonCreate.clicked.connect(self.accept)
        self.buttonCancel.clicked.connect(self.reject)

        intValidator = QIntValidator(0, 99999999, self)
        intValidatorNumRots = QIntValidator(0, 100, self)

        self.inputCodeProduct.setValidator(intValidator)
        self.inputKg.setValidator(intValidator)
        self.inputNumRots.setValidator(intValidatorNumRots)
        
    def accept(self):
    
        codigo = self.inputCodeProduct.text().strip()
        nombre = self.inputNameProduct.text().strip()
        peso = self.inputKg.text().strip()
        num_rotulos = self.inputNumRots.text().strip()

        if not codigo or not nombre or not peso or not num_rotulos:
            QMessageBox.warning(self, "Campos vacíos", "Por favor, complete todos los campos antes de continuar. ❌")
            return

         
        if peso.isdigit() and int(peso) <= 0:
            QMessageBox.warning(self, "Peso inválido", "El peso debe ser mayor a 0. ⚖️")
            return

        if num_rotulos.isdigit() and int(num_rotulos) <= 0:
            QMessageBox.warning(self, "Número inválido", "Debe generar al menos 1 rótulo. 📝")
            return  

        super().accept()


    def getData(self):
        
        return {
            'nombre': self.inputNameProduct.text().strip(),
            'codigo': self.inputCodeProduct.text().strip(),
            'peso': self.inputKg.text().strip(),
            'rotulos': self.inputNumRots.text().strip()
        }