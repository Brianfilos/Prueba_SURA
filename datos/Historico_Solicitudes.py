import pandas as pd
import unicodedata
# Historico_Solicitudes.py
# Lectura y entendimiento del archivo Historico_Solicitudes.csv

# ---- PASO 1: leer el archivo ----
# read_csv convierte el CSV directamente en una tabla
# utf-8-sig lee bien las tildes y descarta una marca invisible al inicio del archivo
hist = pd.read_csv("Historico_Solicitudes.csv", encoding="utf-8-sig")

print("PASO 1 - Lectura del archivo")
print("Filas y columnas:", hist.shape)
print("Columnas:")
for columna in hist.columns:
    print("   ", columna)

# ---- PASO 2: ver un registro completo y los campos vacíos ----
print()
print("PASO 2 - Primer registro")
print(hist.iloc[0])

print()
print("Campos vacíos por columna:")
vacios = hist.isna().sum()
print(vacios[vacios > 0])

# ---- PASO 3: valores de las columnas de clasificación ----
# value_counts() cuenta cuántas veces aparece cada valor
print()
print("PASO 3 - Valores por columna")

print()
print("Canal:")
print(hist["Canal"].value_counts())

print()
print("Prioridad:")
print(hist["Prioridad"].value_counts())

print()
print("Estado:")
print(hist["Estado"].value_counts())

print()
print("Categorías distintas:", hist["Categoria"].nunique())
print("Subcategorías distintas:", hist["Subcategoria"].nunique())

# ---- PASO 4: estandarizar la prioridad contra el catálogo ----
# limpiar() deja el texto en minúsculas y sin tildes, para poder comparar
def limpiar(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = texto.encode("ascii", "ignore").decode()
    return texto.lower().strip()


# Tabla de equivalencias: valor limpio -> prioridad oficial del catálogo
# "urgente" no existe en el catálogo: se asume que equivale a Crítica
mapa_prioridad = {
    "critica": "Crítica",
    "urgente": "Crítica",
    "alta": "Alta",
    "media": "Media",
    "baja": "Baja",
}

hist["PrioridadEstandar"] = hist["Prioridad"].apply(limpiar).map(mapa_prioridad)

print()
print("PASO 4 - Prioridad estandarizada")
print("Valores antes:", hist["Prioridad"].nunique())
print("Valores después:", hist["PrioridadEstandar"].nunique())
print(hist["PrioridadEstandar"].value_counts())
print("Sin equivalencia:", hist["PrioridadEstandar"].isna().sum())

# ---- PASO 5: estandarizar el estado ----
# Además de mayúsculas y tildes, hay sinónimos: Finalizada = Cerrada, Anulada = Cancelada
mapa_estado = {
    "registrada": "Registrada",
    "asignada": "Asignada",
    "asignado": "Asignada",
    "en gestion": "En gestión",
    "en proceso": "En gestión",
    "escalada": "Escalada",
    "escalado": "Escalada",
    "cerrada": "Cerrada",
    "cerrado": "Cerrada",
    "finalizada": "Cerrada",
    "cancelada": "Cancelada",
    "anulada": "Cancelada",
}

hist["EstadoEstandar"] = hist["Estado"].apply(limpiar).map(mapa_estado)

print()
print("PASO 5 - Estado estandarizado")
print("Valores antes:", hist["Estado"].nunique())
print("Valores después:", hist["EstadoEstandar"].nunique())
print(hist["EstadoEstandar"].value_counts())
print("Sin equivalencia:", hist["EstadoEstandar"].isna().sum())

# Hipótesis 1: FechaCierre vacía significa solicitud sin cerrar
print()
print("Solicitudes por estado, con y sin fecha de cierre:")
hist["SinFechaCierre"] = hist["FechaCierre"].isna()
print(pd.crosstab(hist["EstadoEstandar"], hist["SinFechaCierre"]))

# Hipótesis 2: Responsable vacío significa solicitud sin asignar
print()
print("Solicitudes sin responsable, por estado:")
print(hist[hist["Responsable"].isna()]["EstadoEstandar"].value_counts())

# ---- PASO 6: recuperar la categoría oficial a partir de la subcategoría ----
# Se lee el catálogo y se arma un diccionario: subcategoría -> categoría estándar
cat = pd.read_excel("Catalogos_Gobierno.xlsx", sheet_name="Categorias")
sub_a_cat = dict(zip(cat["Subcategoria"], cat["CategoriaEstandar"]))

hist["CategoriaEstandar"] = hist["Subcategoria"].map(sub_a_cat)

print()
print("PASO 6 - Categoría estandarizada")
print("Categorías antes:", hist["Categoria"].nunique())
print("Categorías después:", hist["CategoriaEstandar"].nunique())
print("Subcategorías fuera del catálogo:", hist["CategoriaEstandar"].isna().sum())

# Para cada categoría oficial, todas las formas en que venía escrita
print()
print("Cómo venía escrita cada categoría:")
for categoria, grupo in hist.groupby("CategoriaEstandar"):
    print("   ", categoria, "<-", ", ".join(sorted(grupo["Categoria"].unique())))

# ---- PASO 7: tiempos de atención y cumplimiento del plazo ----
# Las fechas llegan como texto; se convierten para poder restarlas
for columna in ["FechaCreacion", "FechaAsignacion", "FechaObjetivo", "FechaCierre"]:
    hist[columna] = pd.to_datetime(hist[columna])

print()
print("PASO 7 - Tiempos de atención")
print("Periodo:", hist["FechaCreacion"].min(), "a", hist["FechaCreacion"].max())

# Fechas inconsistentes: cierre anterior a la creación
inconsistentes = hist["FechaCierre"] < hist["FechaCreacion"]
print("Cierre anterior a la creación:", inconsistentes.sum())

# Solo se miden las cerradas con fechas coherentes
cerradas = hist[(hist["EstadoEstandar"] == "Cerrada") & ~inconsistentes].copy()

# Horas entre la creación y el cierre
cerradas["HorasAtencion"] = (
    cerradas["FechaCierre"] - cerradas["FechaCreacion"]
).dt.total_seconds() / 3600

# Cumple si se cerró antes de la fecha objetivo
cerradas["Cumple"] = cerradas["FechaCierre"] <= cerradas["FechaObjetivo"]

print("Solicitudes medidas:", len(cerradas))
print("Mediana de atención (horas):", cerradas["HorasAtencion"].median())
print("Cumplimiento del plazo:", round(cerradas["Cumple"].mean() * 100, 1), "%")

# Por prioridad: plazo del catálogo, tiempo real y cumplimiento
print()
print("Por prioridad:")
resumen = cerradas.groupby("PrioridadEstandar").agg(
    Cerradas=("IdSolicitud", "count"),
    PlazoHoras=("SLAHoras", "max"),
    MedianaHoras=("HorasAtencion", "median"),
    Cumplimiento=("Cumple", "mean"),
)
resumen["Cumplimiento"] = (resumen["Cumplimiento"] * 100).round(1)
print(resumen.loc[["Crítica", "Alta", "Media", "Baja"]])

# ---- PASO 8: cuánto tarda la asignación ----
# Horas entre la creación y la asignación a un responsable
hist["HorasAsignacion"] = (
    hist["FechaAsignacion"] - hist["FechaCreacion"]
).dt.total_seconds() / 3600

# Asignación tardía: se asignó cuando el plazo ya había vencido
hist["AsignacionTardia"] = hist["FechaAsignacion"] > hist["FechaObjetivo"]

print()
print("PASO 8 - Tiempo hasta la asignación")
print("Mediana de asignación (horas):", hist["HorasAsignacion"].median())

con_asignacion = hist[hist["FechaAsignacion"].notna()]
asignacion = con_asignacion.groupby("PrioridadEstandar").agg(
    PlazoHoras=("SLAHoras", "max"),
    MedianaAsignacion=("HorasAsignacion", "median"),
    AsignadaYaVencida=("AsignacionTardia", "mean"),
)
asignacion["AsignadaYaVencida"] = (asignacion["AsignadaYaVencida"] * 100).round(1)
print(asignacion.loc[["Crítica", "Alta", "Media", "Baja"]])

# ---- PASO 9: solicitudes abiertas (backlog) ----
# Fecha de corte: la fecha más reciente que aparece en el archivo
fechas = ["FechaCreacion", "FechaAsignacion", "FechaObjetivo", "FechaCierre"]
corte = hist[fechas].max().max()

abiertas = hist[
    hist["EstadoEstandar"].isin(["Registrada", "Asignada", "En gestión", "Escalada"])
].copy()

# Antigüedad: días desde que se creó hasta la fecha de corte
abiertas["DiasAbierta"] = (corte - abiertas["FechaCreacion"]).dt.days

print()
print("PASO 9 - Solicitudes abiertas")
print("Fecha de corte:", corte)
print("Abiertas:", len(abiertas), "de", len(hist))
print("Con el plazo ya vencido:", (abiertas["FechaObjetivo"] < corte).sum())
print("Mediana de antigüedad (días):", abiertas["DiasAbierta"].median())
print("Con más de un año:", (abiertas["DiasAbierta"] > 365).sum())
print("Sin responsable:", abiertas["Responsable"].isna().sum())

# Entradas frente a salidas por mes (se excluye el último mes, que está incompleto)
entran = hist.groupby(hist["FechaCreacion"].dt.to_period("M")).size()
salen = hist.groupby(hist["FechaCierre"].dt.to_period("M")).size()
print()
print("Promedio mensual de solicitudes que entran:", round(entran.iloc[:-1].mean()))
print("Promedio mensual de solicitudes que se cierran:", round(salen.iloc[:-1].mean()))

# ---- PASO 10: responsables contra el catálogo, referencias y guardado ----
resp = pd.read_excel("Catalogos_Gobierno.xlsx", sheet_name="Responsables")

# En el catálogo cada nombre aparece dos veces; solo nombre + equipo identifica a la persona
llaves = set(zip(resp["Responsable"], resp["Equipo"]))
con_resp = hist[hist["Responsable"].notna()]
coincide = [
    (n, e) in llaves for n, e in zip(con_resp["Responsable"], con_resp["Equipo"])
]

print()
print("PASO 10 - Responsables y referencias")
print("Solicitudes con responsable:", len(con_resp))
print("Nombre y equipo coinciden con el catálogo:", sum(coincide))
print("No coinciden (no se sabe cuál persona es):", len(con_resp) - sum(coincide))

# La referencia de origen debería identificar un caso; se mide cuántas se repiten
repetidas = hist["OrigenReferencia"].duplicated(keep=False)
print("Solicitudes que comparten referencia de origen con otra:", repetidas.sum())

# Se guarda la tabla con las columnas estandarizadas
hist.to_csv("Historico_limpio.csv", index=False, encoding="utf-8-sig")
print("Archivo guardado: Historico_limpio.csv")