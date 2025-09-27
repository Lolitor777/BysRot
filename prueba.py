import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===== CONFIGURACIÓN =====
BASE_URL = "https://byspro.heinsohncloud.com.co:50000/b1s/v2"
CREDENTIALS = {
    "UserName": "manager",
    "Password": "2609",
    "CompanyDB": "PRUEBAS_AVANTIS_MAY14"
}

# ===== LOGIN =====
session = requests.Session()
resp = session.post(f"{BASE_URL}/Login", json=CREDENTIALS, verify=False)

if resp.status_code != 200:
    print("❌ Error en login:", resp.text)
    exit()

print("✅ Login exitoso")

# ===== PROBAR ORDEN =====
codigo_producto = "60001199"   # 👈 prueba con un código real que tengas
url = (
    f"{BASE_URL}/ProductionOrders"
    f"?$filter=ProductionOrderStatus eq 'boposPlanned' and ItemNo eq '{codigo_producto}'"
    "&$orderby=DocumentNumber desc&$top=1"
)

resp_order = session.get(url, verify=False)
data_order = resp_order.json()
print("\n==== ORDEN ENCONTRADA ====")
print(json.dumps(data_order, indent=4, ensure_ascii=False))

if "value" in data_order and data_order["value"]:
    order = data_order["value"][0]

    print(f"\n📌 Orden encontrada: {order['DocumentNumber']} - {order['ProductDescription']}")
    print("📦 Materias primas:")
    
    lines = order.get("ProductionOrderLines", [])
    for line in lines:
        print(f"   - {line['ItemNo']} | {line['ItemName']} | Cantidad: {line['PlannedQuantity']}")

    print(f"\n✅ Total materias primas: {len(lines)}")

