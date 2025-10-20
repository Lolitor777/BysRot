from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QWidget, QScrollArea,
                             QMessageBox, QSizePolicy, QHBoxLayout, QFileDialog, QLabel)
from PyQt6.QtCore import Qt
import json

from utils.generarPdf import generar_pdf, generar_pdf_72mm
from utils.storage import guardarPlantilla
from gui.rotuloWidget import RotuloWidget
from utils.sapService import sap



class RotWindow(QDialog):
    def __init__(self, data, loadedPath=None):
        super().__init__()
        self.data = data or {}
        self.loadedPath = loadedPath

        self.doc_entry = self.data.get("doc_entry")
        self.estado_orden = self.data.get("estado_orden", "boposPlanned")

       
        self.setWindowTitle("BysRot")
        self.resize(600, 700)
        self.setFixedWidth(600)
        self.setMinimumHeight(700)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # Contenedores
        self.rotulos = []
        self.labelCount = QLabel("Total rótulos: 0", self)
        self.labelCount.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(scrollWidget)
        self.scrollLayout.addStretch()
        scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea.setWidget(scrollWidget)

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.scrollArea)

        # Botones
        btnLayoutTop = QHBoxLayout()
        btnLayoutBottom = QHBoxLayout()
        self.btnAdd = QPushButton("Añadir rótulo ➕")
        self.btnSave = QPushButton("Guardar plantilla 📁")
        self.btnPdf = QPushButton("Generar PDF 📋")
        self.btnLiberar = QPushButton("Liberar orden 🔓")
        self.btnEntregar = QPushButton("Entregar componentes 📦")

        

        for btn in (self.btnAdd, self.btnSave, self.btnPdf, self.btnLiberar, self.btnEntregar):
            btn.setFixedSize(150, 40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setDefault(False)
            btn.setAutoDefault(False)

        self.btnAdd.clicked.connect(lambda: self.addRotulo(comunes=self.comunes if hasattr(self, "comunes") else None))
        self.btnSave.clicked.connect(self.saveTemplate)
        self.btnPdf.clicked.connect(self.generatePdf)
        self.btnLiberar.clicked.connect(self.liberarOrden)
        self.btnEntregar.clicked.connect(self.entregarComponentes)

        if self.estado_orden == "boposReleased":
            self.btnLiberar.setEnabled(False)
            self.btnEntregar.setEnabled(True)   
        else:
            self.btnLiberar.setEnabled(True)
            self.btnEntregar.setEnabled(False)

        btnLayoutTop.addWidget(self.btnAdd)
        btnLayoutTop.addWidget(self.btnSave)
        btnLayoutTop.addWidget(self.btnPdf)

        btnLayoutBottom.addWidget(self.btnLiberar)
        btnLayoutBottom.addWidget(self.btnEntregar)

        mainLayout.addWidget(self.labelCount)
        mainLayout.addLayout(btnLayoutTop)
        mainLayout.addLayout(btnLayoutBottom)


        self.setLayout(mainLayout)

        self.btnSave.setEnabled(False)

        
        self.comunes = self.data.get("comunes") or {
            "fecha": self.data.get("fecha", ""),
            "nombre": self.data.get("nombre", ""),
            "codigo": self.data.get("codigo", ""),
            "lote": self.data.get("lote", ""),
            "firma": ""
        }


        # 🔥 Crear rótulos desde la plantilla
        if isinstance(self.data.get("rotulos"), list):
            for mp in self.data["rotulos"]:
                if isinstance(mp, dict):
                    if "codigo" in mp and "cantidad" in mp:
                        # Datos directos desde SAP
                        self.addRotulo(rot_data={
                            "codigoMateriaPrima": mp["codigo"],
                            "peso": str(mp["cantidad"])
                        })
                    else:
                        
                        self.addRotulo(rot_data=mp)

    
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
            
            ruta_58 = ruta.replace(".pdf", "_72mm.pdf")
            generar_pdf_72mm(ruta_58, self.rotulos)

            QMessageBox.information(
                self,
                "Éxito",
                f"Se generaron los PDF correctamente ✅\n\n"
                f"- Normal: {ruta}\n"
                f"- 72mm: {ruta_58}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron generar los PDF ❌\n{e}"
            )

    # ---------- conectar cambios ----------
    def _connectChanges(self, rotulo):
        rotulo.dateChanged.connect(self.syncDate)
        rotulo.nameChanged.connect(self.syncName)
        rotulo.codeChanged.connect(self.syncCode)
        rotulo.batchChanged.connect(self.syncBatch)
        rotulo.signatureChanged.connect(self.syncSignature)

        # para habilitar guardar cuando cambian campos individuales
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
        if hasattr(rotulo, "checkSyncDate"):
            rotulo.checkSyncDate.stateChanged.connect(self.enableSave)

    def enableSave(self):
        self.btnSave.setEnabled(True)

    def addRotulo(self, rot_data=None, comunes=None):
        comunes = comunes or self.comunes
        index = len(self.rotulos) + 1
        rotulo = RotuloWidget(index)

        insert_pos = max(0, self.scrollLayout.count() - 1)
        self.scrollLayout.insertWidget(insert_pos, rotulo)
        self.rotulos.append(rotulo)
        self._connectChanges(rotulo)

        if hasattr(rotulo, "deleteRequested"):
            rotulo.deleteRequested.connect(self.removeRotulo)

        # Aplicar comunes
        rotulo.setDate(comunes.get("fecha", ""))
        rotulo.setName(comunes.get("nombre", ""))
        rotulo.setCode(comunes.get("codigo", ""))
        rotulo.setBatch(comunes.get("lote", ""))
        rotulo.setSignature(comunes.get("firma", ""))

        # Aplicar datos individuales si hay
        if isinstance(rot_data, dict):
            if "codigoMateriaPrima" in rot_data:
                rotulo.inputCodeMateriaPrima.setText(rot_data["codigoMateriaPrima"])
                if rot_data["codigoMateriaPrima"] and rot_data["codigoMateriaPrima"] != "1000":
                    rotulo.autofillFromSAP()

            if "peso" in rot_data:
                rotulo.inputPesoNeto.setText(rot_data["peso"])

            if "numControl" in rot_data:
                rotulo.inputNumControl.setText(rot_data["numControl"])

            if rot_data.get("fechaIndependiente"):
                rotulo.inputDate.setText(rot_data.get("fecha", ""))

        self.enableSave()
        self.updateRotuloCount()
        return rotulo



    def removeRotulo(self, rotulo):
        if rotulo in self.rotulos:
            self.rotulos.remove(rotulo)
            rotulo.setParent(None)
            rotulo.deleteLater()
            self.enableSave()
            self.updateRotuloCount()

    
    def getTemplateData(self):
        if not self.rotulos:
            return {}

        # Buscar el primer rótulo con datos comunes válidos
        rot0 = None
        for r in self.rotulos:
            if (hasattr(r, "inputDate") and r.inputDate.text()) or \
            (hasattr(r, "inputName") and r.inputName.text()) or \
            (hasattr(r, "inputCode") and r.inputCode.text()) or \
            (hasattr(r, "inputBatch") and r.inputBatch.text()):
                rot0 = r
                break

        if not rot0:
            rot0 = self.rotulos[0]

        comunes = {
            "fecha": rot0.inputDate.text() if hasattr(rot0, 'inputDate') else "",
            "nombre": rot0.inputName.text() if hasattr(rot0, 'inputName') else "",
            "codigo": rot0.inputCode.text() if hasattr(rot0, 'inputCode') else "",
            "lote": rot0.inputBatch.text() if hasattr(rot0, 'inputBatch') else "",
            "firma": rot0.inputSignature.text() if hasattr(rot0, 'inputSignature') else ""
        }

        rotulos = []
        rotulos = [rot.getData() for rot in self.rotulos]
        return {'comunes': comunes, 
                'rotulos': rotulos, 
                'doc_entry': self.doc_entry, 
                'estado_orden': self.estado_orden
                }


    
    def saveTemplate(self):
        template = self.getTemplateData()
        if not template:
            return
        if self.loadedPath:
            try:
                with open(self.loadedPath, "w", encoding="utf-8") as f:
                    json.dump(template, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "Éxito", "La plantilla se actualizó correctamente ✅")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar la plantilla ❌ {e}")
                return
        else:
            codigo = self.data.get("codigo", "").strip()
            nombre = self.data.get("nombrePlantilla", "").strip()
            peso = self.data.get("peso", "").strip()
            filename = f"{codigo} - {nombre} - {peso}kg"
            guardarPlantilla(filename, template)
            QMessageBox.information(self, "Éxito", "La plantilla se guardó correctamente ✅")

        # tras guardar: marcar como "sin cambios"
        self.btnSave.setEnabled(False)

    # ---------- sincronizaciones ----------
    def syncDate(self, newDate):
        sender = self.sender()
        if hasattr(sender, "isDateSynced") and sender.isDateSynced():
            for r in self.rotulos:
                if r.isDateSynced():
                    r.setDate(newDate)

    def syncName(self, newName):
        for r in self.rotulos:
            r.setName(newName)

    def syncCode(self, newCode):
        for r in self.rotulos:
            r.setCode(newCode)

    def syncBatch(self, newBatch):
        for r in self.rotulos:
            r.setBatch(newBatch)

    def syncSignature(self, newSignature):
        for r in self.rotulos:
            r.setSignature(newSignature)

    def updateRotuloCount(self):
        self.labelCount.setText(f"Total rótulos: {len(self.rotulos)}")

    # ---------- cierre con advertencia ----------
    def closeEvent(self, event):
        if self.btnSave.isEnabled():
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle("Salir")
            msgBox.setText("Tienes cambios sin guardar. ¿Qué deseas hacer?")
            msgBox.setIcon(QMessageBox.Icon.Warning)
            btnGuardar = msgBox.addButton("Guardar y salir", QMessageBox.ButtonRole.AcceptRole)
            btnSalir = msgBox.addButton("Salir sin guardar", QMessageBox.ButtonRole.DestructiveRole)
            btnCancelar = msgBox.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
            msgBox.setDefaultButton(btnGuardar)
            msgBox.exec()
            clicked = msgBox.clickedButton()
            if clicked == btnGuardar:
                self.saveTemplate()
                event.accept()
            elif clicked == btnSalir:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def scrollToWidget(self, widget):
        self.scrollArea.ensureWidgetVisible(widget)

    
    def liberarOrden(self):

        if not self.doc_entry:
            QMessageBox.warning(self, "Error", "No se encontró el DocEntry de la orden ❌")
            return

        try:
            ok = sap.liberar_orden(self.doc_entry)
            if ok:
                self.estado_orden = "boposReleased"
                self.btnLiberar.setEnabled(False)
                self.btnEntregar.setEnabled(True)  # 🔒 Se deshabilita
                QMessageBox.information(self, "Éxito", f"La orden {self.doc_entry} fue liberada ✅")
            else:
                QMessageBox.critical(self, "Error", f"No se pudo liberar la orden {self.doc_entry}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error liberando la orden:\n{e}")


    def entregarComponentes(self):
        if not self.doc_entry:
            QMessageBox.warning(self, "Error", "No se encontró el DocEntry de la orden ❌")
            return

        seleccionados = []
        for rot in self.rotulos:
            if hasattr(rot, "checkEntregar") and rot.checkEntregar.isChecked():
                seleccionados.append({
                    "codigoMateriaPrima": rot.inputCodeMateriaPrima.text(),
                    "peso": rot.inputPesoNeto.text(),
                })

        if not seleccionados:
            QMessageBox.warning(self, "Atención", "Debe seleccionar al menos un rótulo para entregar.")
            return

        try:
            result = sap.entregar_componentes(self.doc_entry, seleccionados)
            QMessageBox.information(self, "Éxito", f"Se entregaron los componentes ✅\nDocNum SAP: {result.get('DocNum')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error en la entrega:\n{e}")
