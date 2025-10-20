from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIntValidator
from PyQt6 import uic
from PyQt6.QtCore import Qt, QEvent

from utils.sapService import SAPService
from absoluteRouts import resource_path


sap = SAPService(
    user="manager",
    password="2609",
    company_db="SBOLabAvantis",
    base_url="https://byspro.heinsohncloud.com.co:50000/b1s/v2"
)


class RotuloWidget(QWidget):
    # Señales
    dateChanged = pyqtSignal(str)
    nameChanged = pyqtSignal(str)
    codeChanged = pyqtSignal(str)
    batchChanged = pyqtSignal(str)
    signatureChanged = pyqtSignal(str)
    useGlobalDate = pyqtSignal(bool)
    deleteRequested = pyqtSignal(QWidget)

    def __init__(self, numberRot):
        super().__init__()
        self.numberRot = numberRot
        uic.loadUi(resource_path('gui/rotuloWidget.ui'), self)

        # Botón borrar sin default
        self.btnDelete.setDefault(False)
        self.btnDelete.setAutoDefault(False)

        # Código MP
        if hasattr(self, 'inputCodeMateriaPrima'):
            self.inputCodeMateriaPrima.setText("1000")
            self.inputCodeMateriaPrima.returnPressed.connect(self.autofillFromSAP)
            self.inputCodeMateriaPrima.editingFinished.connect(self.autofillFromSAP)

        # Conexiones de cambios
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

        # Fecha global
        if hasattr(self, 'checkUseGlobalDate'):
            self.checkUseGlobalDate.setChecked(True)
            self.checkUseGlobalDate.stateChanged.connect(self.emitUseGlobalDate)
        
        # Rotulo para entrega
        if hasattr(self, 'checkEntregar'):
            self.checkEntregar.setChecked(True)

        # Validadores
        if hasattr(self, 'inputTara'):
            validator = QIntValidator(0, 9999999, self)  # extendido
            self.inputTara.setValidator(validator)
            self.inputTara.installEventFilter(self)

        if hasattr(self, 'inputPesoNeto'):
            validator = QIntValidator(0, 9999999, self)
            self.inputPesoNeto.setValidator(validator)

        # Actualización peso bruto
        if hasattr(self, 'inputTara') and hasattr(self, 'inputPesoNeto') and hasattr(self, 'inputPesoBruto'):
            self.inputTara.textChanged.connect(self.updatePesoBruto)
            self.inputPesoNeto.textChanged.connect(self.updatePesoBruto)

        # Eliminar rótulo
        if hasattr(self, "btnDelete"):
            self.btnDelete.clicked.connect(self.requestDelete)

    # ----------------- SAP autofill -----------------
    def autofillFromSAP(self):
        """Rellena automáticamente los datos de la materia prima desde SAP"""
        codigo = self.inputCodeMateriaPrima.text().strip()
        if not codigo:
            return

        try:
            data = sap.get_item_and_batches(codigo)
            if not data:
                return

            if hasattr(self, "inputMateriaPrima"):
                self.inputMateriaPrima.setText(data.get("nombre", ""))

            if hasattr(self, "inputBatchMateriaPrima"):
                self.inputBatchMateriaPrima.setText(data.get("lote", ""))

            # Número de control
            ultimos4 = codigo[-4:] if len(codigo) >= 4 else codigo
            fecha = data.get("fechaIngreso", "")
            num_control = f"{ultimos4}{fecha}" if fecha else ultimos4

            if hasattr(self, "inputNumControl"):
                self.inputNumControl.setText(num_control)

        except Exception as e:
            print(f"Error en autofillFromSAP: {e}")

    # ----------------- Emisores -----------------
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
        self.useGlobalDate.emit(self.checkUseGlobalDate.isChecked())

    # ----------------- Lógica pesos -----------------
    def updatePesoBruto(self):
        try:
            tara = float(self.inputTara.text() or 0)
            neto = float(self.inputPesoNeto.text() or 0)
            bruto = tara + neto
            self.inputPesoBruto.setText(f"{bruto:.2f}")
        except ValueError:
            self.inputPesoBruto.clear()

    # ----------------- Setters -----------------
    def setDate(self, text):
        if hasattr(self, "inputDate") and self.inputDate.text() != text:
            self.inputDate.setText(text)

    def setName(self, text):
        if hasattr(self, "inputName") and self.inputName.text() != text:
            self.inputName.setText(text)

    def setCode(self, text):
        if hasattr(self, "inputCode") and self.inputCode.text() != text:
            self.inputCode.setText(text)

    def setMateriaPrimaCode(self, codigo: str):
        if hasattr(self, "inputCodeMateriaPrima"):
            self.inputCodeMateriaPrima.setText(codigo.strip())
            # no llamamos autofill aquí -> se activará con editingFinished

    def setBatch(self, text):
        if hasattr(self, "inputBatch") and self.inputBatch.text() != text:
            self.inputBatch.setText(text)

    def setSignature(self, text):
        if hasattr(self, "inputSignature") and self.inputSignature.text() != text:
            self.inputSignature.setText(text)

    # ----------------- Estado -----------------
    def usesGlobalDate(self):
        return hasattr(self, 'checkUseGlobalDate') and self.checkUseGlobalDate.isChecked()

    def isDateSynced(self):
        if hasattr(self, "checkSyncDate"):
            return self.checkSyncDate.isChecked()
        return True

    # ----------------- Eliminar -----------------
    def requestDelete(self):
        self.deleteRequested.emit(self)

    # ----------------- Navegación Tab -----------------
    def eventFilter(self, obj, event):
        if obj is getattr(self, "inputTara", None) and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Tab:
                self.focusNextTara()
                return True
            if event.key() == Qt.Key.Key_Backtab:
                self.focusPrevTara()
                return True
        return super().eventFilter(obj, event)

    def focusNextTara(self):
        rot_window = self.window()
        if hasattr(rot_window, "rotulos"):
            idx = rot_window.rotulos.index(self)
            if idx < len(rot_window.rotulos) - 1:
                next_tara = rot_window.rotulos[idx + 1].inputTara
                next_tara.setFocus()
                if hasattr(rot_window, "scrollToWidget"):
                    rot_window.scrollToWidget(next_tara)

    def focusPrevTara(self):
        rot_window = self.window()
        if hasattr(rot_window, "rotulos"):
            idx = rot_window.rotulos.index(self)
            if idx > 0:
                prev_tara = rot_window.rotulos[idx - 1].inputTara
                prev_tara.setFocus()
                if hasattr(rot_window, "scrollToWidget"):
                    rot_window.scrollToWidget(prev_tara)

    
    def getData(self):
        return {
            "materiaPrima": self.inputMateriaPrima.text() if hasattr(self, 'inputMateriaPrima') else "",
            "loteMateriaPrima": self.inputBatchMateriaPrima.text() if hasattr(self, 'inputBatchMateriaPrima') else "",
            "codigoMateriaPrima": self.inputCodeMateriaPrima.text() if hasattr(self, 'inputCodeMateriaPrima') else "",
            "numControl": self.inputNumControl.text() if hasattr(self, 'inputNumControl') else "",
            "peso": self.inputPesoNeto.text() if hasattr(self, 'inputPesoNeto') else "",
            "fechaIndependiente": not self.isDateSynced(),
            "fecha": self.inputDate.text() if hasattr(self, 'inputDate') else "",
            "entregar": self.checkEntregar.isChecked() if hasattr(self, "checkEntregar") else True,
            "usarFechaGlobal": self.checkUseGlobalDate.isChecked() if hasattr(self, "checkUseGlobalDate") else True
        }

