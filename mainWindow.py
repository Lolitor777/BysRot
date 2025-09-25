import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QDialog, QFileDialog, QMessageBox)
from PyQt6 import uic
from gui.createWindow import CreateWindow
from gui.rotWindow import RotWindow
from absoluteRouts import resource_path


class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path('gui/mainWindow.ui'), self)

        self.createTemplate.clicked.connect(self.openCreateWindow)
        self.loadTemplate.clicked.connect(self.openLoadTemplate)

    def openCreateWindow(self):
        self.createWindow = CreateWindow()
        result = self.createWindow.exec()

        if result == QDialog.DialogCode.Accepted:
            data = self.createWindow.getData()

            rotWindow = RotWindow(data)
            result_rot = rotWindow.exec()

            if result_rot == QDialog.DialogCode.Accepted:
                self.show()

    def openLoadTemplate(self):
        carpeta = os.path.join(os.path.expanduser("~"), "Documents", "BysRot", "plantillas")
        os.makedirs(carpeta, exist_ok=True)

        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Cargar plantilla",
            carpeta,
            "Plantillas JSON (*.json)"
        )

        if not ruta:
            return 

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                template = json.load(f)
            
            rotWindow = RotWindow(template, loadedPath=ruta)
            rotWindow.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la plantilla:\n{e}")
                


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()