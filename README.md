# Pipeline de Analítica e Ingeniería de Datos: Gestión de Inventario para MiPymes (Medellín)

## 1. Definición de Negocio (Hito 1)
* **Problemática:** Las micro, pequeñas y medianas empresas (MiPymes) del sector comercial en Medellín y el Valle de Aburrá suelen gestionar su inventario de forma manual, generando quiebres de stock en productos de alta rotación, exceso de capital inmovilizado y desconocimiento del impacto cambiario (TRM) en sus costos de reposición.
* **Usuario Objetivo:** Gerentes operativos, administradores y encargados de compras de MiPymes comercializadoras.
* **Pregunta de Negocio:** *¿Qué productos presentan riesgo crítico de quiebre de stock o sobreinventario en nuestras bodegas de Medellín, y cómo impacta la fluctuación de la TRM en el costo de reposición?*

## 2. Arquitectura y Fuentes de Datos
* **API 1 (Catálogo y Movimientos):** DummyJSON (`https://dummyjson.com/products` y `https://dummyjson.com/carts`) para extraer niveles de stock, precios en USD, pedidos mínimos y salidas históricas.
* **API 2 (Contexto Económico Colombia):** Datos Abiertos Colombia - Socrata (`https://www.datos.gov.co/resource/32sa-8pi3.json`) para obtener la TRM oficial vigente y valorizar el inventario en COP.
* **Fuente Externa Complementaria:** Maestro local de bodegas y proveedores en el Valle de Aburrá (`data/external/bodegas_medellin.csv`) con tiempos de entrega (*Lead Time*) y costos operativos.

## 3. Modelo Dimensional (Esquema Estrella)
* **`fact_inventario` (Tabla de Hechos):** `id_registro` (PK), `id_producto` (FK), `id_bodega` (FK), `fecha_corte` (FK), `stock_actual`, `unidades_vendidas`, `costo_unitario_usd`, `valor_inventario_cop`.
* **`dim_producto` (Dimensión):** `id_producto` (PK), `nombre_producto`, `categoria`, `marca`, `precio_usd`, `stock_minimo`, `estado_disponibilidad`.
* **`dim_bodega` (Dimensión):** `id_bodega` (PK), `nombre_bodega`, `zona_medellin`, `proveedor_principal`, `lead_time_dias`, `costo_almacenamiento_cop`.
* **`dim_calendario_trm` (Dimensión):** `fecha_corte` (PK), `trm_cop`, `anio`, `mes`, `mes_nombre`.

## 4. Indicadores Clave (KPIs - Medidas DAX)
1. **Valor Total del Inventario (COP):** Valorización total del stock disponible según la TRM vigente.
2. **Stock Total en Unidades:** Inventario físico acumulado en bodegas.
3. **SKUs en Riesgo de Quiebre:** Conteo de productos con `stock_actual < stock_minimo`.
4. **Tasa de Quiebre de Stock (%):** Porcentaje del catálogo en alerta crítica de desabastecimiento.
5. **Índice de Rotación de Inventario:** Relación entre unidades vendidas y stock disponible.
6. **Días de Cobertura Estimados:** Proyección de duración del inventario actual según la demanda promedio.

## 5. Gestión y Roles del Proyecto
* **Ingesta y Extracción (APIs):** Consumo automatizado de endpoints REST con paginación, control de errores HTTP y respaldo crudo (`src/01_ingesta_apis.py`).
* **Transformación y Limpieza (Python/Pandas):** Aplanamiento de JSON, manejo de valores nulos, tipado de datos y cruce relacional (`src/02_transformacion.py`).
* **Modelado Dimensional y DAX:** Construcción del esquema estrella (cardinalidades `1:N`), validación de integridad referencial y creación de métricas en Power BI.
* **Visualización BI y Storytelling:** Diseño de tablero ejecutivo interactivo de 2 vistas (Resumen Financiero y Detalle Operativo de Reposición).
