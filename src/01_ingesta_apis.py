import json
import os
import requests

# Crear directorios si no existen
os.makedirs("data/raw", exist_ok=True)


def descargar_api(url, nombre_archivo, params=None):
  try:
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()  # Lanza error si el código no es 200
    datos = response.json()

    ruta_salida = f"data/raw/{nombre_archivo}"
    with open(ruta_salida, "w", encoding="utf-8") as f:
      json.dump(datos, f, ensure_ascii=False, indent=4)

    print(f"[OK] {nombre_archivo} guardado correctamente.")
    return datos
  except requests.exceptions.RequestException as e:
    print(f"[ERROR] Falló la descarga de {url}: {e}")
    return None


if __name__ == "__main__":
  # 1. Endpoint Productos (con paginación limit=100 para traer catálogo amplio)
  descargar_api(
      "https://dummyjson.com/products", "products_raw.json", params={"limit": 100}
  )

  # 2. Endpoint Carritos (simula movimientos de salida/ventas)
  descargar_api(
      "https://dummyjson.com/carts", "carts_raw.json", params={"limit": 50}
  )

  # 3. API Datos Abiertos Colombia - TRM Oficial (Socrata)
  descargar_api(
      "https://www.datos.gov.co/resource/32sa-8pi3.json",
      "trm_colombia_raw.json",
      params={"$limit": 30, "$order": "vigenciahasta DESC"},
  )