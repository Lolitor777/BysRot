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

        lines_url = f"{self.base_url}/ProductionOrders({doc_entry})?$select=ProductionOrderLines"
        

        resp_lines = self.session.get(lines_url, verify=False)
        lines_data = resp_lines.json()

        materias_primas = []
        if "ProductionOrderLines" in lines_data:
            for line in lines_data["ProductionOrderLines"]:
                materias_primas.append(line.get("ItemNo"))

        count_lines = 0
        if "ProductionOrderLines" in lines_data:
            count_lines = len(lines_data["ProductionOrderLines"])

        return {
            "codigo": order.get("ItemNo"),
            "nombre": order.get("ProductDescription"),
            "cantidad_rotulos": count_lines,
            "materias_primas": materias_primas
        }




