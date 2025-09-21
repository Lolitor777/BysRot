
from PyQt6.QtWidgets import (QDialog,  QVBoxLayout, QPushButton, QWidget, QScrollArea,
                             QMessageBox, QSizePolicy, QHBoxLayout, QFileDialog)
from PyQt6.QtCore import Qt

import json

from src.utils.generarPdf import generar_pdf
from src.utils.storage import guardarPlantilla
from src.gui.rotuloWidget import RotuloWidget


class RotWindow(QDialog):
    def __init__(self, data, loadedPath=None):
        super().__init__()
        self.data = data
        self.loadedPath = loadedPath
        

        self.setWindowTitle("BysRot")
        self.resize(600, 700)

        self.setFixedWidth(600)
        self.setMinimumHeight(700)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)


        self.rotulos = []

        scrollArea = QScrollArea(self)
        scrollArea.setWidgetResizable(True)
        scrollWidget = QWidget()
        scrollLayout = QVBoxLayout(scrollWidget)

        if isinstance(data.get("rotulos"), str) or isinstance(data.get("rotulos"), int):
            try:
                numRots = int(data.get("rotulos", "1"))
            except ValueError:
                numRots = 1
            comunes = {}
            rotulos = [{} for _ in range(numRots)]
        else:
            comunes = data.get("comunes", {})
            rotulos = data.get("rotulos", [])

        scrollLayout.addStretch()
        scrollWidget.setLayout(scrollLayout)
        scrollArea.setWidget(scrollWidget)
        
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(scrollArea)

        btnLayout = QHBoxLayout()


        self.btnSave = QPushButton('Guardar plantilla')
        self.btnSave.setFixedSize(150, 40)
        self.btnSave.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnSave.clicked.connect(self.saveTemplate)
        
        self.btnPdf = QPushButton("Generar PDF")
        self.btnPdf.setFixedSize(150, 40)
        self.btnPdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnPdf.clicked.connect(self.generatePdf)

        btnLayout.addWidget(self.btnSave)
        btnLayout.addWidget(self.btnPdf)


        mainLayout.addLayout(btnLayout)
        self.setLayout(mainLayout)

        self.btnSave.setEnabled(False)


        for i, rot_data in enumerate(rotulos, start=1):
            rotulo = RotuloWidget(i)
            self.rotulos.append(rotulo)
            scrollLayout.addWidget(rotulo)

            self._connectChanges(rotulo)

            if comunes:
                if rotulo.isDateSynced():  
                    rotulo.setDate(comunes.get("fecha", ""))
                rotulo.setName(comunes.get("nombre", ""))
                rotulo.setCode(comunes.get("codigo", ""))
                rotulo.setBatch(comunes.get("lote", ""))
                rotulo.setSignature(comunes.get("firma", ""))

            if rot_data:
                if hasattr(rotulo, "inputMateriaPrima"):
                    rotulo.inputMateriaPrima.setText(rot_data.get("materiaPrima", ""))
                if hasattr(rotulo, "inputBatchMateriaPrima"):
                    rotulo.inputBatchMateriaPrima.setText(rot_data.get("loteMateriaPrima", ""))
                if hasattr(rotulo, "inputCodeMateriaPrima"):
                    rotulo.inputCodeMateriaPrima.setText(rot_data.get("codigoMateriaPrima", ""))
                if hasattr(rotulo, "inputNumControl"):
                    rotulo.inputNumControl.setText(rot_data.get("numControl", ""))
                if hasattr(rotulo, "inputPesoNeto"):
                    rotulo.inputPesoNeto.setText(rot_data.get("peso", ""))

                if "fechaIndependiente" in rot_data and hasattr(rotulo, "checkSyncDate"):
                    rotulo.checkSyncDate.setChecked(not rot_data["fechaIndependiente"])
                if "fecha" in rot_data and hasattr(rotulo, "inputDate"):
                    rotulo.inputDate.setText(rot_data.get("fecha", ""))

            if hasattr(rotulo, "checkSyncDate"):
                rotulo.checkSyncDate.stateChanged.connect(self.enableSave)

            rotulo.dateChanged.connect(self.syncDate)
            rotulo.nameChanged.connect(self.syncName)
            rotulo.codeChanged.connect(self.syncCode)
            rotulo.batchChanged.connect(self.syncBatch)
            rotulo.signatureChanged.connect(self.syncSignature)


    def generatePdf(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar PDF",
            "rotulos.pdf",
            "Archivos PDF (*.pdf)"
        )
        if not ruta:
            return

        try:
            generar_pdf(ruta, self.rotulos)
            QMessageBox.information(self, "Éxito", f"PDF generado correctamente ✅")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el PDF ❌\n{e}")
            print(e)

    def _connectChanges(self, rotulo):
        if hasattr(rotulo, "inputDate"):
            rotulo.inputDate.textChanged.connect(self.enableSave)
        if hasattr(rotulo, "inputName"):
            rotulo.inputName.textChanged.connect(self.enableSave)
        if hasattr(rotulo, "inputCode"):
            rotulo.inputCode.textChanged.connect(self.enableSave)
        if hasattr(rotulo, "inputBatch"):
            rotulo.inputBatch.textChanged.connect(self.enableSave)
        if hasattr(rotulo, "inputSignature"):
            rotulo.inputSignature.textChanged.connect(self.enableSave)
    
    def enableSave(self):
        self.btnSave.setEnabled(True)

   

    def getTemplateData(self):
        if not self.rotulos:
            return {}
        
        rot0 = self.rotulos[0]
        comunes = {
            "fecha":rot0.inputDate.text() if hasattr(rot0, 'inputDate') else "",
            "nombre":rot0.inputName.text() if hasattr(rot0, 'inputName') else "",
            "codigo":rot0.inputCode.text() if hasattr(rot0, 'inputCode') else "",
            "lote":rot0.inputBatch.text() if hasattr(rot0, 'inputBatch') else "",
            "firma":rot0.inputSignature.text() if hasattr(rot0, 'inputSignature') else ""
        }

        rotulos = []
        for rot in self.rotulos:
            rotulos.append({
                "materiaPrima": rot.inputMateriaPrima.text() if hasattr(rot, 'inputMateriaPrima') else "",
                "loteMateriaPrima": rot.inputBatchMateriaPrima.text() if hasattr(rot, 'inputBatchMateriaPrima') else "",
                "codigoMateriaPrima": rot.inputCodeMateriaPrima.text() if hasattr(rot, 'inputCodeMateriaPrima') else "",
                "numControl": rot.inputNumControl.text() if hasattr(rot, 'inputNumControl') else "",
                "peso": rot.inputPesoNeto.text() if hasattr(rot, 'inputPesoNeto') else "",
                "fechaIndependiente": not rot.isDateSynced(),  
                "fecha": rot.inputDate.text() if hasattr(rot, 'inputDate') else ""
            })
    
        
        return {
            'comunes': comunes,
            'rotulos': rotulos
        }
    
    def saveTemplate(self):
        template = self.getTemplateData()
        if not template:
            return

        if self.loadedPath:
            try:
                with open(self.loadedPath, "w", encoding="utf-8") as f:
                    json.dump(template, f, ensure_ascii=False, indent=4)
                
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"La plantilla se actualizó correctamente ✅"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"No se pudo actualizar la plantilla ❌ {e}"
                )
                return
            
        else:
            codigo = self.data.get("codigo", "").strip()
            nombre = self.data.get("nombre", "").strip()
            peso = self.data.get("peso", "").strip()

            filename = f"{codigo} - {nombre} - {peso}kg"
            
            guardarPlantilla(filename, template)
            
            QMessageBox.information(
                self,
                "Éxito",
                f"La plantilla se guardó correctamente ✅"
            )

        
    def syncDate(self, newDate):
        sender = self.sender()

        if hasattr(sender, "isDateSynced") and sender.isDateSynced():
            for rotulo in self.rotulos:
                if rotulo.isDateSynced():
                    rotulo.setDate(newDate)

        else:
            pass
    
    def syncName(self, newName):
        for rotulo in self.rotulos:
            rotulo.setName(newName)

    def syncCode(self, newCode):
        for rotulo in self.rotulos:
            rotulo.setCode(newCode)

    def syncBatch(self, newBatch):
        for rotulo in self.rotulos:
            rotulo.setBatch(newBatch)

    def syncSignature(self, newSignature):
        for rotulo in self.rotulos:
            rotulo.setSignature(newSignature)