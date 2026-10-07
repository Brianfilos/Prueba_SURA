import pandas as pd
# Catalogos_Gobierno.py
# Lectura y entendimiento del archivo Catalogos_Gobierno.xlsx

# ---- PASO 1: abrir el libro y ver qué hojas tiene ----
# ExcelFile abre el libro sin cargar todavía los datos
libro = pd.ExcelFile("Catalogos_Gobierno.xlsx")

print("PASO 1 - Hojas del libro")
print("Hojas:", libro.sheet_names)

# ---- PASO 2: leer cada hoja y ver su tamaño y sus columnas ----
# parse() convierte una hoja en una tabla
print()
print("PASO 2 - Estructura de cada hoja")
for hoja in libro.sheet_names:
    tabla = libro.parse(hoja)
    print()
    print("Hoja:", hoja)
    print("   Filas y columnas:", tabla.shape)
    print("   Columnas:", list(tabla.columns))
    print("   Campos vacíos:", tabla.isna().sum().sum())

# ---- PASO 3: catálogo de SLA (tiempos de atención) ----
# Son solo 4 filas, así que se imprime la hoja completa
sla = libro.parse("SLA")

print()
print("PASO 3 - Catálogo de SLA")
print(sla.to_string(index=False))

# ---- PASO 4: catálogo de responsables (quién puede atender) ----
resp = libro.parse("Responsables")

print()
print("PASO 4 - Catálogo de responsables")
print("Primeras 5 filas:")
print(resp.head().to_string(index=False))

print()
print("Personas en el catálogo:", len(resp))
print("Nombres distintos:", resp["Responsable"].nunique())
print("Correos distintos:", resp["Correo"].nunique())

print()
print("Activos e inactivos:")
print(resp["Activo"].value_counts())

print()
print("Personas inactivas:")
print(resp[resp["Activo"] == "No"].to_string(index=False))

# ---- PASO 5: catálogo de categorías (cómo se clasifica) ----
cat = libro.parse("Categorias")

print()
print("PASO 5 - Catálogo de categorías")
print("Primeras 5 filas:")
print(cat.head().to_string(index=False))

print()
print("Categorías estándar:", cat["CategoriaEstandar"].nunique())
print("Subcategorías:", cat["Subcategoria"].nunique())

# groupby agrupa las filas por categoría; aquí se listan las subcategorías de cada una
print()
print("Subcategorías por categoría:")
for categoria, grupo in cat.groupby("CategoriaEstandar"):
    print("   ", categoria, "->", ", ".join(grupo["Subcategoria"]))

# ---- PASO 6: capacidad disponible por especialidad ----
# Solo se cuentan las personas activas
activos = resp[resp["Activo"] == "Sí"]

# Por cada especialidad: cuántas personas hay y cuánta capacidad diaria suman
capacidad = activos.groupby("Especialidad").agg(
    Personas=("Responsable", "count"),
    CapacidadDiaria=("CapacidadDiaria", "sum"),
)

print()
print("PASO 6 - Capacidad por especialidad (solo activos)")
print(capacidad)
print()
print("Capacidad diaria total (activos):", activos["CapacidadDiaria"].sum())
print(
    "Capacidad que se pierde por inactivos:",
    resp[resp["Activo"] == "No"]["CapacidadDiaria"].sum(),
)

# Se comprueba que las especialidades sean las mismas 8 categorías del catálogo
iguales = set(resp["Especialidad"]) == set(cat["CategoriaEstandar"])
print("¿Las especialidades coinciden con las categorías?", iguales)