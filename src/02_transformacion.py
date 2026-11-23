import json
import os
import numpy as np
import pandas as pd

os.makedirs("data/processed", exist_ok=True)

# 1. Cargar datos crudos
with open("data/raw/products_raw.json", "r", encoding="utf-8") as f:
  prod_raw = json.load(f)["products"]

with open("data/raw/carts_raw.json", "r", encoding="utf-8") as f:
  carts_raw = json.load(f)["carts"]

with open("data/raw/trm_colombia_raw.json", "r", encoding="utf-8") as f:
  trm_raw = json.load(f)

df_bodegas = pd.read_csv("data/external/bodegas_medellin.csv")

# --- TABLA 1: DIM_PRODUCTO ---
df_prod = pd.json_normalize(prod_raw)
dim_producto = df_prod[[
    "id",
    "title",
    "category",
    "brand",
    "price",
    "minimumOrderQuantity",
    "availabilityStatus",
]].copy()
dim_producto.columns = [
    "id_producto",
    "nombre_producto",
    "categoria",
    "marca",
    "precio_usd",
    "stock_minimo",
    "estado_disponibilidad",
]
dim_producto["marca"] = dim_producto["marca"].fillna("Genérico / Sin Marca")
dim_producto["stock_minimo"] = dim_producto["stock_minimo"].fillna(10).astype(int)

# --- TABLA 2: DIM_BODEGA ---
dim_bodega = df_bodegas.copy()

# --- TABLA 3: DIM_CALENDARIO_TRM ---
df_trm = pd.DataFrame(trm_raw)
df_trm["fecha_corte"] = pd.to_datetime(df_trm["vigenciahasta"]).dt.date
df_trm["trm_cop"] = df_trm["valor"].astype(float)
dim_calendario = (
    df_trm[["fecha_corte", "trm_cop"]]
    .drop_duplicates(subset=["fecha_corte"])
    .sort_values("fecha_corte")
)
dim_calendario["anio"] = pd.to_datetime(dim_calendario["fecha_corte"]).dt.year
dim_calendario["mes"] = pd.to_datetime(dim_calendario["fecha_corte"]).dt.month
dim_calendario["mes_nombre"] = pd.to_datetime(
    dim_calendario["fecha_corte"]
).dt.strftime("%B")

# --- TABLA 4: FACT_INVENTARIO_MOVIMIENTOS ---
ventas_list = []
for cart in carts_raw:
  for item in cart["products"]:
    ventas_list.append(
        {"id_producto": item["id"], "unidades_vendidas": item["quantity"]}
    )

df_ventas = (
    pd.DataFrame(ventas_list)
    .groupby("id_producto", as_index=False)["unidades_vendidas"]
    .sum()
)

fact_inv = df_prod[["id", "stock", "price"]].copy()
fact_inv.columns = ["id_producto", "stock_actual", "costo_unitario_usd"]
fact_inv = fact_inv.merge(df_ventas, on="id_producto", how="left")
fact_inv["unidades_vendidas"] = fact_inv["unidades_vendidas"].fillna(0).astype(int)

np.random.seed(42)
fact_inv["id_bodega"] = np.random.randint(1, 5, size=len(fact_inv))
fecha_actual = dim_calendario["fecha_corte"].max()
trm_actual = dim_calendario.loc[
    dim_calendario["fecha_corte"] == fecha_actual, "trm_cop"
].values[0]

fact_inv["fecha_corte"] = fecha_actual
fact_inv["id_registro"] = range(1, len(fact_inv) + 1)
fact_inv["valor_inventario_cop"] = (
    fact_inv["stock_actual"] * fact_inv["costo_unitario_usd"] * trm_actual
).round(2)

fact_inv = fact_inv[[
    "id_registro",
    "id_producto",
    "id_bodega",
    "fecha_corte",
    "stock_actual",
    "unidades_vendidas",
    "costo_unitario_usd",
    "valor_inventario_cop",
]]

# Exportar tablas limpias
dim_producto.to_csv("data/processed/dim_producto.csv", index=False)
dim_bodega.to_csv("data/processed/dim_bodega.csv", index=False)
dim_calendario.to_csv("data/processed/dim_calendario_trm.csv", index=False)
fact_inv.to_csv("data/processed/fact_inventario.csv", index=False)

print("[OK] Modelo Estrella exportado en data/processed/")