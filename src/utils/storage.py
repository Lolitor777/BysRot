import os
import json

def guardarPlantilla(nombre, datos):
    documentos = os.path.join(os.path.expanduser("~"), "Documents", "BysRot", "plantillas")
    os.makedirs(documentos, exist_ok=True)

    ruta = os.path.join(documentos, f"{nombre}_plantilla.json")

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

    return ruta