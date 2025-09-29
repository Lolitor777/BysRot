from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtGui import QIntValidator
from PyQt6 import uic
from absoluteRouts import resource_path
from utils.sapService import SAPService
 
sap = SAPService(
    user="manager",
    password="2609",
    company_db="PRUEBAS_AVANTIS_MAY14",
    base_url="https://byspro.heinsohncloud.com.co:50000/b1s/v2"
)

class CreateWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path('gui/createWindow.ui'), self)
        self.latest_order = None
        self.nameProduct = ""

        self.buttonCreate.clicked.connect(self.accept)
        self.buttonCancel.clicked.connect(self.reject)

        intValidator = QIntValidator(0, 99999999, self)
        self.inputCodeProduct.setValidator(intValidator)
        self.inputKg.setValidator(intValidator)

        # Conectar signals para búsqueda automática
        self.inputCodeProduct.editingFinished.connect(self.fetchProductionOrder)
        self.inputCodeProduct.returnPressed.connect(self.fetchProductionOrder)
        self.inputCodeProduct.textChanged.connect(self.on_code_changed)

    def on_code_changed(self, text):
        """Limpiar orden anterior si el campo se vacía"""
        if not text.strip():
            self.latest_order = None

    def accept(self):
        codigo = self.inputCodeProduct.text().strip()
        nombre = self.inputNameProduct.text().strip()
        peso = self.inputKg.text().strip()
        
        if "/" in nombre:
            QMessageBox.warning(self, "Caracter erroneo","Windows no permite guardar archivo con el caracter '/'. ❌")
            return

        if not codigo or not nombre or not peso:
            QMessageBox.warning(self, "Campos vacíos", "Por favor, complete todos los campos antes de continuar. ❌")
            return

        if peso.isdigit() and int(peso) <= 0:
            QMessageBox.warning(self, "Peso inválido", "El peso debe ser mayor a 0. ⚖️")
            return

        if not self.latest_order:
            self.fetchProductionOrder()
            if not self.latest_order:
                QMessageBox.warning(self, "Orden faltante", "Debe consultar una orden de producción válida antes de continuar.")
                return

        super().accept()

    def fetchProductionOrder(self):
        codigo_producto = self.inputCodeProduct.text().strip()
        
        if not codigo_producto:
            self.latest_order = None
            return
            
        # Solo buscar si el código tiene la longitud adecuada (ajusta según tus códigos)
        if len(codigo_producto) < 6:
            self.latest_order = None
            return

        try:
            order = sap.get_latest_planned_order(codigo_producto)
            
            if not order:
                QMessageBox.warning(self, "SAP", f"No se encontró una orden planeada para el código: {codigo_producto}")
                self.latest_order = None
                return

            self.latest_order = order
            cantidad = order.get('cantidad_rotulos', 0)
            self.nameProduct = order.get('nombre', 'N/A')

            QMessageBox.information(
                self, "Orden encontrada ✅",
                f"Producto: {self.nameProduct}\n"
                f"Código: {order.get('codigo', 'N/A')}\n"
                f"Se generarán {cantidad} rótulos (materias primas)."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error SAP", f"Error al consultar SAP: {str(e)}")
            self.latest_order = None

    def getData(self):
        materias_primas = []
        if self.latest_order and "cantidad_rotulos" in self.latest_order:
            cantidad_rotulos = self.latest_order["cantidad_rotulos"]
            materias_primas = self.latest_order.get("materias_primas", [])
        
        return {
            'nombrePlantilla': self.inputNameProduct.text().strip(),
            'nombre': self.nameProduct,
            'codigo': self.inputCodeProduct.text().strip(),
            'peso': self.inputKg.text().strip(),
            "rotulos": materias_primas 
        }