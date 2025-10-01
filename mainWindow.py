import sys
import json
import traceback
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QDialog, QFileDialog, QMessageBox
)
from PyQt6 import uic

from gui.createWindow import CreateWindow
from gui.rotWindow import RotWindow
from absoluteRouts import resource_path


class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path("gui/mainWindow.ui"), self)

        # Botones
        self.createTemplate.clicked.connect(self.openCreateWindow)
        self.loadTemplate.clicked.connect(self.openLoadTemplate)

    def openCreateWindow(self):
        """Abrir ventana para crear una nueva plantilla"""
        create_window = CreateWindow()
        if create_window.exec() == QDialog.DialogCode.Accepted:
            data = create_window.getData()
            rot_window = RotWindow(data)
            rot_window.exec()

    def openLoadTemplate(self):
        """Abrir plantilla existente en formato JSON"""
        carpeta = Path.home() / "Documents" / "BysRot" / "plantillas"
        carpeta.mkdir(parents=True, exist_ok=True)

        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Cargar plantilla",
            str(carpeta),
            "Plantillas JSON (*.json)"
        )

        if not ruta:
            return

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                template = json.load(f)

            rot_window = RotWindow(template, loadedPath=ruta)
            rot_window.exec()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar la plantilla:\n{e}"
            )
            # 🔥 Para depuración (opcional, puedes quitarlo en producción)
            print("Error al cargar plantilla:")
            traceback.print_exc()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
