import requests
import urllib3
from datetime import datetime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SAPService:
    def __init__(self, user, password, company_db, base_url):
        self.user = user
        self.password = password
        self.company_db = company_db
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.logged_in = False
        self.login()

    def login(self):
        login_url = f"{self.base_url}/Login"
        credentials = {
            "UserName": self.user,
            "Password": self.password,
            "CompanyDB": self.company_db
        }
        resp = self.session.post(login_url, json=credentials, verify=False)
        
        print(resp.status_code, resp.text)

        if resp.status_code == 200:
            self.logged_in = True
        else:
            raise Exception(f"Error al iniciar sesión en SAP: {resp.text}")

    def get_item_and_batches(self, item_code, top=1):
        if not self.logged_in:
            self.login()

        
        item_url = f"{self.base_url}/Items?$filter=ItemCode eq '{item_code}'&$select=ItemCode,ItemName"
        item_resp = self.session.get(item_url, verify=False)
        item_data = item_resp.json()
        if "value" not in item_data or not item_data["value"]:
            return None

        item = item_data["value"][0]
        
        batches_url = f"{self.base_url}/BatchNumberDetails?$filter=ItemCode eq '{item_code}'&$orderby=AdmissionDate desc&$top={top}"
        batches_resp = self.session.get(batches_url, verify=False)
        batches_data = batches_resp.json()

        batch = None
        if "value" in batches_data and batches_data["value"]:
            batch = batches_data["value"][0]

        fecha_formateada = ""
        if batch and batch.get("AdmissionDate"):
            try:
                fecha_obj = datetime.strptime(batch["AdmissionDate"], "%Y-%m-%d")
                fecha_formateada = fecha_obj.strftime("%d%m%y")  # DDMMYY
            except Exception:
                fecha_formateada = batch["AdmissionDate"]

        return {
            "codigo": item.get("ItemCode", ""),
            "nombre": item.get("ItemName", ""),
            "lote": batch.get("Batch", "") if batch else "",
            "fechaIngreso": fecha_formateada
        }
    

    def get_latest_planned_order(self, item_code):
        if not self.logged_in:
            self.login()

        url = (
            f"{self.base_url}/ProductionOrders"
            f"?$filter=ProductionOrderStatus eq 'boposPlanned' and ItemNo eq '{item_code}'"
            "&$orderby=DocumentNumber desc&$top=1"
        )
        resp = self.session.get(url, verify=False)
        data = resp.json()
        if "value" not in data or not data["value"]:
            return None

        order = data["value"][0]
        doc_entry = order.get("AbsoluteEntry")

        # pedir líneas con cantidades
        lines_url = f"{self.base_url}/ProductionOrders({doc_entry})?$select=ProductionOrderLines,ProductionOrderStatus,PlannedQuantity"
        resp_lines = self.session.get(lines_url, verify=False)
        lines_data = resp_lines.json()

        materias_primas = []
        if "ProductionOrderLines" in lines_data:
            for line in lines_data["ProductionOrderLines"]:
                materias_primas.append({
                    "codigo": line.get("ItemNo"),
                    "cantidad": line.get("PlannedQuantity", 0)   # cantidad planificada de esa MP
                })

        return {
            "codigo": order.get("ItemNo"),
            "nombre": order.get("ProductDescription"),
            "lote": order.get("Warehouse"),   # aquí depende de tu SAP: si tienes Batch/Lote asociado
            "cantidad_rotulos": len(materias_primas),
            "materias_primas": materias_primas,
            "cantidad_final": lines_data.get("PlannedQuantity", 0),  # cantidad del producto final
            "doc_entry": doc_entry,
            "estado_orden": lines_data.get("ProductionOrderStatus", "boposPlanned") 
        }
    

    def liberar_orden(self, doc_entry: int):
        url = f"{self.base_url}/ProductionOrders({doc_entry})"
        payload = {
            "ProductionOrderStatus": "boposReleased"
        }
        resp = self.session.patch(url, json=payload, verify=False)
        if resp.status_code == 204:
            return True
        else:
            raise Exception(f"Error liberando orden {doc_entry}: {resp.text}")


    

    def entregar_componentes(self, doc_entry: int, rotulos: list):
    

        if not self.logged_in:
            self.login()

        movimientos = []

        for rot in rotulos:
            codigo = rot.get("codigoMateriaPrima")
            cantidad = float(rot.get("peso", 0) or 0)
            if not codigo or cantidad <= 0:
                continue

            # 🔎 Buscar el lote más viejo disponible (AdmissionDate asc)
            lote_url = (
                f"{self.base_url}/BatchNumberDetails?"
                f"$filter=ItemCode eq '{codigo}' and Quantity gt 0 and Warehouse eq '04' "
                f"&$orderby=AdmissionDate asc"
            )
            lote_resp = self.session.get(lote_url, verify=False).json()

            if "value" not in lote_resp or not lote_resp["value"]:
                raise Exception(f"No se encontró lote disponible con stock para el item {codigo}")

            lote = lote_resp["value"][0]["Batch"]

            movimientos.append({
                "ItemCode": codigo,
                "Quantity": cantidad,
                "WarehouseCode": "04",   
                "AccountCode": '1410',
                "BatchNumbers": [
                    {"BatchNumber": lote, "Quantity": cantidad}
                ]
            })

        if not movimientos:
            raise Exception("No se generaron líneas para la entrega")

        payload = {
            "DocDate": datetime.now().strftime("%Y-%m-%d"),
            "Comments": f"Consumo automático desde BysRot. Orden {doc_entry}",
            "JournalMemo": f"Consumo OF {doc_entry}",
            # Relacionar con la orden (si tu versión soporta esto)
            "U_BYSROT_OF": doc_entry,   # 🔥 Puedes usar un campo de usuario para trazar
            "DocumentLines": movimientos
        }

        url = f"{self.base_url}/InventoryGenExits"
        resp = self.session.post(url, json=payload, verify=False)

        if resp.status_code in (200, 201):
            return resp.json()
        else:
            raise Exception(f"Error en entrega: {resp.status_code} {resp.text}")
        


sap = SAPService(
    user="manager",   
    password="2609",  
    company_db="SBOLabAvantis",
    base_url="https://byspro.heinsohncloud.com.co:50000/b1s/v2"
)





    
    






