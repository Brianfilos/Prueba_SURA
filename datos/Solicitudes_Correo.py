import pandas as pd
# Solicitudes_Correo.py
# Lectura y entendimiento del archivo Solicitudes_Correo.xlsx

# ---- PASO 1: leer el archivo ----
correo = pd.read_excel("Solicitudes_Correo.xlsx")

print("PASO 1 - Lectura del archivo")
print("Filas y columnas:", correo.shape)
print("Columnas:")
for columna in correo.columns:
    print("   ", columna)

# ---- PASO 2: ver un mensaje completo y los campos vacíos ----
print()
print("PASO 2 - Primer mensaje")
primero = correo.iloc[0]
for columna in correo.columns:
    print("   ", columna, "=", primero[columna])

print()
print("Campos vacíos por columna:")
vacios = correo.isna().sum()
print(vacios[vacios > 0])

# ---- PASO 3: mensajes duplicados e hilos de conversación ----
print()
print("PASO 3 - Duplicados e hilos")

# Duplicado: el mismo Message ID aparece más de una vez
print("Mensajes en el archivo:", len(correo))
print("Message ID distintos:", correo["Message ID"].nunique())
print("Mensajes repetidos:", correo["Message ID"].duplicated().sum())

# ¿Son copias exactas? Se comparan todas las columnas, no solo el Id
print("Filas idénticas en todas las columnas:", correo.duplicated().sum())

# Hilo: varios mensajes comparten el mismo Conversation ID
print()
print("Hilos distintos:", correo["Conversation ID"].nunique())
tamano = correo.groupby("Conversation ID").size()
print("Hilos según cuántos mensajes tienen:")
print(tamano.value_counts().sort_index())

# Se quitan los duplicados exactos para seguir trabajando
correo = correo.drop_duplicates()
print()
print("Mensajes después de quitar duplicados:", len(correo))

# ---- PASO 4: prefijos del asunto (respuestas y reenvíos) ----
# str.extract saca el prefijo si el asunto empieza por RE: o RV:
correo["Prefijo"] = correo["Subject"].str.extract(r"^(RE|RV):")[0].fillna("Sin prefijo")

# El asunto base es el asunto sin el prefijo
correo["AsuntoBase"] = correo["Subject"].str.replace(r"^(RE|RV):\s*", "", regex=True)

print()
print("PASO 4 - Asuntos")
print("Mensajes por prefijo:")
print(correo["Prefijo"].value_counts())

print()
print("Asuntos distintos:", correo["Subject"].nunique())
print("Asuntos distintos sin el prefijo:", correo["AsuntoBase"].nunique())

print()
print("Los 5 asuntos más frecuentes:")
print(correo["AsuntoBase"].value_counts().head(5))

# ---- PASO 5: revisar el cuerpo de los mensajes ----
# El cuerpo trae saltos de línea; se reemplazan por espacios para leerlo en una sola línea
correo["Cuerpo"] = correo["Body"].str.replace(r"\s+", " ", regex=True).str.strip()

print()
print("PASO 5 - Cuerpo de los mensajes")
print("Cuerpos distintos:", correo["Cuerpo"].nunique())

# Se toma el comienzo de cada cuerpo para agrupar las plantillas
correo["Inicio"] = correo["Cuerpo"].str[:32]
print()
print("Comienzos más frecuentes:")
print(correo["Inicio"].value_counts().head(12))

# Un ejemplo completo de los tres comienzos más frecuentes
print()
print("Ejemplos:")
for inicio in correo["Inicio"].value_counts().head(3).index:
    ejemplo = correo[correo["Inicio"] == inicio]["Cuerpo"].iloc[0]
    print()
    print("   ", ejemplo)

# ---- PASO 6: clasificar cada mensaje por lo que dice su cuerpo ----
def tipo_mensaje(cuerpo):
    if "caso resuelto" in cuerpo:
        return "Cierre"
    if "alguna actualización" in cuerpo:
        return "Seguimiento"
    if "Dando continuidad" in cuerpo:
        return "Continuidad de otro canal"
    return "Solicitud"


correo["TipoMensaje"] = correo["Cuerpo"].apply(tipo_mensaje)

print()
print("PASO 6 - Tipo de mensaje según el cuerpo")
print(correo["TipoMensaje"].value_counts())

# Cruce: lo que dice el cuerpo frente al prefijo del asunto
print()
print("Tipo de mensaje frente al prefijo del asunto:")
print(pd.crosstab(correo["TipoMensaje"], correo["Prefijo"]))

# Solicitud nueva: el cuerpo pide algo y el asunto no es respuesta ni reenvío
nuevas = (correo["TipoMensaje"] == "Solicitud") & (correo["Prefijo"] == "Sin prefijo")
print()
print("Solicitudes nuevas:", nuevas.sum(), "de", len(correo))
print("No son solicitudes nuevas:", (~nuevas).sum())

# ---- PASO 7: hilos, relación con el histórico y guardado ----
print()
print("PASO 7 - Hilos y relación con el histórico")

# ¿Los mensajes de un mismo hilo hablan del mismo asunto?
mensajes_por_hilo = correo.groupby("Conversation ID").size()
asuntos_por_hilo = correo.groupby("Conversation ID")["AsuntoBase"].nunique()
con_varios = mensajes_por_hilo > 1
print("Hilos con más de un mensaje:", con_varios.sum())
print("De esos, hilos que mezclan asuntos distintos:", (con_varios & (asuntos_por_hilo > 1)).sum())

# ¿Cuántos de estos correos ya están registrados en el histórico?
# El histórico guarda el Message ID en la columna OrigenReferencia
hist = pd.read_csv("Historico_Solicitudes.csv", encoding="utf-8-sig")
correo["EnHistorico"] = correo["Message ID"].isin(hist["OrigenReferencia"])

print()
print("Correos que ya aparecen en el histórico:", correo["EnHistorico"].sum())
print("Solicitudes nuevas ya registradas:", (nuevas & correo["EnHistorico"]).sum())
print("Solicitudes nuevas sin registrar:", (nuevas & ~correo["EnHistorico"]).sum())

# Se guarda la tabla con las columnas nuevas
correo.drop(columns="Inicio").to_csv("Correo_limpio.csv", index=False, encoding="utf-8-sig")
print()
print("Archivo guardado: Correo_limpio.csv")
