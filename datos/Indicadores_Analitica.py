import pandas as pd

# Indicadores del entregable 5, calculados sobre el histórico ya limpio.
# Usa las mismas definiciones de Historico_Solicitudes.py (pasos 7 a 9).

# ---- PASO 1: leer el histórico limpio ----
hist = pd.read_csv("Historico_limpio.csv")
for columna in ["FechaCreacion", "FechaAsignacion", "FechaObjetivo", "FechaCierre"]:
    hist[columna] = pd.to_datetime(hist[columna])

print("PASO 1 - Lectura")
print("Solicitudes:", len(hist))
print("Periodo:", hist["FechaCreacion"].min(), "a", hist["FechaCreacion"].max())

# ---- PASO 2: volumen y evolución por periodo ----
hist["Anio"] = hist["FechaCreacion"].dt.year
hist["Mes"] = hist["FechaCreacion"].dt.to_period("M")
por_mes = hist.groupby("Mes").size()

print()
print("PASO 2 - Volumen por periodo")
print(hist.groupby("Anio").size())
print("Meses con datos:", len(por_mes))
print("Promedio mensual:", round(por_mes.mean(), 1))
print("Mes más bajo y más alto:", por_mes.min(), "y", por_mes.max())

# ---- PASO 3: distribución por canal, categoría, prioridad y estado ----
print()
print("PASO 3 - Distribución")
for columna in ["Canal", "CategoriaEstandar", "PrioridadEstandar", "EstadoEstandar"]:
    conteo = hist[columna].value_counts()
    tabla = pd.DataFrame({"Solicitudes": conteo, "Porcentaje": (conteo / len(hist) * 100).round(1)})
    print()
    print(tabla)

# ---- PASO 4: backlog y antigüedad ----
fechas = ["FechaCreacion", "FechaAsignacion", "FechaObjetivo", "FechaCierre"]
corte = hist[fechas].max().max()
abiertas = hist[hist["EstadoEstandar"].isin(["Registrada", "Asignada", "En gestión", "Escalada"])].copy()
abiertas["DiasAbierta"] = (corte - abiertas["FechaCreacion"]).dt.days
tramos = pd.cut(abiertas["DiasAbierta"], [-1, 90, 365, 100000], labels=["Hasta 90 días", "91 días a un año", "Más de un año"])

print()
print("PASO 4 - Backlog y antigüedad")
print("Fecha de corte:", corte)
print("Abiertas:", len(abiertas))
print(tramos.value_counts().sort_index())
print("Abiertas por categoría:")
print(abiertas["CategoriaEstandar"].value_counts())

# ---- PASO 5: demanda frente a capacidad ----
dias = (hist["FechaCreacion"].max() - hist["FechaCreacion"].min()).days + 1
catalogo = pd.read_excel("Catalogos_Gobierno.xlsx", sheet_name=None)
responsables = [hoja for hoja in catalogo.values() if "CapacidadDiaria" in hoja.columns][0]
activos = responsables[responsables["Activo"].astype(str).str.strip().str.lower().isin(["sí", "si", "true", "1"])]

print()
print("PASO 5 - Demanda frente a capacidad")
print("Días del periodo:", dias)
print("Solicitudes por día:", round(len(hist) / dias, 1))
print("Capacidad diaria nominal de activos (supuesto):", activos["CapacidadDiaria"].sum())

# ---- PASO 6: tiempo promedio y percentiles de atención ----
inconsistentes = hist["FechaCierre"] < hist["FechaCreacion"]
cerradas = hist[(hist["EstadoEstandar"] == "Cerrada") & ~inconsistentes].copy()
cerradas["HorasAtencion"] = (cerradas["FechaCierre"] - cerradas["FechaCreacion"]).dt.total_seconds() / 3600

print()
print("PASO 6 - Tiempos de atención")
print("Solicitudes medidas:", len(cerradas))
print("Promedio (horas):", round(cerradas["HorasAtencion"].mean(), 1))
print(cerradas["HorasAtencion"].quantile([0.5, 0.75, 0.9, 0.95]).round(1))

# ---- PASO 7: cumplimiento del plazo ----
cerradas["Cumple"] = cerradas["FechaCierre"] <= cerradas["FechaObjetivo"]

print()
print("PASO 7 - Cumplimiento del plazo")
print("General:", round(cerradas["Cumple"].mean() * 100, 1), "%")
print((cerradas.groupby("PrioridadEstandar")["Cumple"].mean() * 100).round(1))
print("Por canal:")
print((cerradas.groupby("Canal")["Cumple"].mean() * 100).round(1))

# ---- PASO 8: solicitudes recurrentes y principales causas ----
print()
print("PASO 8 - Recurrentes y causas")
print("Subcategorías más pedidas:")
print(hist["Subcategoria"].value_counts().head(8))
print("Observaciones más frecuentes:")
print(hist["Observaciones"].value_counts().head(8))
repetidas = hist["OrigenReferencia"].duplicated(keep=False) & hist["OrigenReferencia"].notna()
print("Comparten referencia de origen:", repetidas.sum())

# ---- PASO 9: cuellos de botella ----
print()
print("PASO 9 - Puntos de acumulación")
print("Mediana de asignación (horas):", hist["HorasAsignacion"].median())
print("Sin responsable:", hist["Responsable"].isna().sum())
print("Abiertas por estado:")
print(abiertas["EstadoEstandar"].value_counts())
