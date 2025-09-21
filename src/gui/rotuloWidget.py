from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIntValidator
from PyQt6 import uic

class RotuloWidget(QWidget):

    dateChanged = pyqtSignal(str)
    nameChanged = pyqtSignal(str)
    codeChanged = pyqtSignal(str)
    batchChanged = pyqtSignal(str)
    signatureChanged = pyqtSignal(str)
    useGlobalDate = pyqtSignal(bool)
    

    def __init__(self, numberRot):
        super().__init__()
        self.numberRot = numberRot
        uic.loadUi('src/gui/rotuloWidget.ui', self)

        
        if hasattr(self, 'inputDate'):
            self.inputDate.textChanged.connect(self.emitDate)

        if hasattr(self, 'inputName'):
            self.inputName.textChanged.connect(self.emitName)

        if hasattr(self, 'inputCode'):
            self.inputCode.textChanged.connect(self.emitCode)

        if hasattr(self, 'inputBatch'):
            self.inputBatch.textChanged.connect(self.emitBatch)

        if hasattr(self, 'inputSignature'):
            self.inputSignature.textChanged.connect(self.emitSignature)
    
        if hasattr(self, 'checkUseGlobalDate'):
            self.checkUseGlobalDate.setChecked(True)
            self.checkUseGlobalDate.stateChanged.connect(self.emitUseGlobalDate)

        if hasattr(self, 'inputTara'):
            validator = QIntValidator(0, 999999, self) 
            self.inputTara.setValidator(validator)

        if hasattr(self, 'inputPesoNeto'):
            validator = QIntValidator(0, 999999, self)
            self.inputPesoNeto.setValidator(validator)

        if hasattr(self, 'inputTara') and hasattr(self, 'inputPesoNeto') and hasattr(self, 'inputPesoBruto'):
            self.inputTara.textChanged.connect(self.updatePesoBruto)
            self.inputPesoNeto.textChanged.connect(self.updatePesoBruto)


    def emitDate(self, text: str):
        self.dateChanged.emit(text)

    def emitName(self, text: str):
        self.nameChanged.emit(text)

    def emitCode(self, text: str):
        self.codeChanged.emit(text)

    def emitBatch(self, text: str):
        self.batchChanged.emit(text)

    def emitSignature(self, text: str):
        self.signatureChanged.emit(text)

    def emitUseGlobalDate(self, state):
        self.useGlobalDateChanged.emit(self.checkUseGlobalDate.isChecked())

    def updatePesoBruto(self):
        try:
            tara = int(self.inputTara.text()) if self.inputTara.text() else 0
            neto = int(self.inputPesoNeto.text()) if self.inputPesoNeto.text() else 0
            bruto = tara + neto
            self.inputPesoBruto.setText(str(bruto) + " g")
        except ValueError:
            self.inputPesoBruto.setText("")

    def setDate(self, text):
        if hasattr(self, "inputDate"):
            if self.inputDate.text() != text:  
                self.inputDate.setText(text)

    def setName(self, text):
        if hasattr(self, "inputName") and self.inputName.text() != text:
            self.inputName.setText(text)

    def setCode(self, text):
        if hasattr(self, "inputCode") and self.inputCode.text() != text:
            self.inputCode.setText(text)

    def setBatch(self, text):
        if hasattr(self, "inputBatch") and self.inputBatch.text() != text:
            self.inputBatch.setText(text)

    def setSignature(self, text):
        if hasattr(self, "inputSignature") and self.inputSignature.text() != text:
            self.inputSignature.setText(text)

    def usesGlobalDate(self):
        return hasattr(self, 'checkUseGlobalDate') and self.checkUseGlobalDate.isChecked()
    
    def isDateSynced(self):
        if hasattr(self, "checkSyncDate"):
            return self.checkSyncDate.isChecked()
        return True