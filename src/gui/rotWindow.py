
from PyQt6.QtWidgets import (QDialog,  QVBoxLayout, QPushButton, QWidget, QScrollArea,)
from src.utils.storage import guardarPlantilla
from src.gui.rotuloWidget import RotuloWidget

class RotWindow(QDialog):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setWindowTitle("BysRot")
        self.resize(600, 800)

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


        for i, rot_data in enumerate(rotulos, start=1):
            rotulo = RotuloWidget(i)
            self.rotulos.append(rotulo)
            scrollLayout.addWidget(rotulo)

            if comunes:
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


            rotulo.dateChanged.connect(self.syncDate)
            rotulo.nameChanged.connect(self.syncName)
            rotulo.codeChanged.connect(self.syncCode)
            rotulo.batchChanged.connect(self.syncBatch)
            rotulo.signatureChanged.connect(self.syncSignature)

        scrollLayout.addStretch()
        scrollWidget.setLayout(scrollLayout)
        scrollArea.setWidget(scrollWidget)
        
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(scrollArea)

        btnSave = QPushButton('Guardar plantilla')
        btnSave.clicked.connect(self.saveTemplate)
        mainLayout.addWidget(btnSave)

        self.setLayout(mainLayout)


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
                "peso": rot.inputPesoNeto.text() if hasattr(rot, 'inputPesoNeto') else ""
            })
    
        
        return {
            'comunes': comunes,
            'rotulos': rotulos
        }
    
    def saveTemplate(self):
        template = self.getTemplateData()
        if not template:
            return
        
        nombre = template["comunes"].get("nombre", "plantilla")
        ruta = guardarPlantilla(nombre, template)
        print(f"Plantilla guardada en: {ruta}")
        
        self.accept()
        
    def syncDate(self, newDate):
        for rotulo in self.rotulos:
            rotulo.setDate(newDate)
    
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