import pandas as pd
# Comunidad_Prestacion.py
# Lectura y entendimiento del archivo Comunidad_Prestacion.txt

#---- PASO 1: abrir el archivo y leerlo completo ----
with open("Comunidad_Prestacion.txt", encoding="utf-8") as archivo:
    texto = archivo.read()

print("PASO 1 - Lectura del archivo")
print("Caracteres leídos:", len(texto))

# ---- PASO 2: revisar las líneas para identificar el patrón ----
# splitlines() convierte el texto en una lista, una posición por línea
lineas = texto.splitlines()

print()
print("PASO 2 - Estructura por líneas")
print("Líneas en el archivo:", len(lineas))
print("Primeras 11 líneas (una publicación y su separador):")
for linea in lineas[:11]:
    print("   ", linea)

# ---- PASO 3: separar el texto en publicaciones ----
# Cada publicación termina con el separador ---
# strip() quita espacios y saltos de línea sobrantes
# "if b.strip()" descarta el bloque vacío que queda después del último ---
bloques = texto.split("---")
bloques = [b.strip() for b in bloques if b.strip()]

print()
print("PASO 3 - Separación en publicaciones")
print("Publicaciones encontradas:", len(bloques))
print("Primera:", bloques[0].splitlines()[0])
print("Última: ", bloques[-1].splitlines()[0])

# ---- PASO 4: identificar los campos de una publicación ----
# Se toma la primera publicación y se numeran sus líneas
primera = bloques[0].splitlines()

print()
print("PASO 4 - Campos de una publicación")
print("Líneas por publicación:", len(primera))
for numero, linea in enumerate(primera):
    print("   ", numero, "->", linea)

# Se comprueba que las 500 publicaciones tengan las mismas 10 líneas
distintas = [b for b in bloques if len(b.splitlines()) != 10]
print("Publicaciones con otra cantidad de líneas:", len(distintas))

# ---- PASO 5: extraer los 10 campos de cada publicación ----
publicaciones = []

for bloque in bloques:
    lineas = bloque.splitlines()
    publicacion = {}

    # Línea 0: el consecutivo, sin la palabra PUBLICACIÓN
    publicacion["Id"] = lineas[0].replace("PUBLICACIÓN", "").strip()

    # Líneas 1 a 6: tienen la forma "Campo: valor"
    # split(":", 1) parte solo en el primer ":" para no romper la hora 07:30
    for linea in lineas[1:7]:
        campo, valor = linea.split(":", 1)
        publicacion[campo.strip()] = valor.strip()

    # Línea 8: el contenido está en la línea siguiente a "Contenido:"
    publicacion["Contenido"] = lineas[8].strip()

    # Línea 9: dos campos en una sola línea, separados por "|"
    comentarios, reacciones = lineas[9].split("|")
    publicacion["Comentarios"] = int(comentarios.split(":")[1])
    publicacion["Reacciones"] = int(reacciones.split(":")[1])

    publicaciones.append(publicacion)

print()
print("PASO 5 - Extracción de campos")
print("Registros creados:", len(publicaciones))
print("Campos por registro:", len(publicaciones[0]))
print("Primer registro:")
for campo, valor in publicaciones[0].items():
    print("   ", campo, "=", valor)

# ---- PASO 6: convertir los registros en una tabla ----
# Un DataFrame de pandas es una tabla: filas = publicaciones, columnas = campos
tabla = pd.DataFrame(publicaciones)

# La fecha llega como texto; se convierte a fecha para poder ordenar y filtrar
tabla["Fecha"] = pd.to_datetime(tabla["Fecha"])

print()
print("PASO 6 - Tabla de publicaciones")
print("Filas y columnas:", tabla.shape)
print()
print("Tipo de dato de cada columna:")
print(tabla.dtypes)
print()
print("Campos vacíos por columna:")
print(tabla.isna().sum())
print()
print("Rango de fechas:", tabla["Fecha"].min(), "a", tabla["Fecha"].max())

# ---- PASO 7: valores distintos de las columnas de clasificación ----
# value_counts() cuenta cuántas veces aparece cada valor
print()
print("PASO 7 - Valores por columna")

print()
print("Tipo de publicación:")
print(tabla["Tipo"].value_counts())

print()
print("Tema:")
print(tabla["Tema"].value_counts())

print()
print("Autores distintos:", tabla["Autor"].nunique())
print("Correos distintos:", tabla["Correo"].nunique())
print("Títulos distintos:", tabla["Título"].nunique())
print("Contenidos distintos:", tabla["Contenido"].nunique())

# ---- PASO 8: revisar los contenidos más repetidos ----
print()
print("PASO 8 - Contenidos más repetidos")
repetidos = tabla["Contenido"].value_counts().head(5)
for contenido, veces in repetidos.items():
    print()
    print(veces, "veces:")
    print("   ", contenido)

# Se toma el comienzo de cada contenido para agrupar las plantillas
tabla["Inicio"] = tabla["Contenido"].str[:25]
print()
print("Comienzos de contenido más frecuentes:")
print(tabla["Inicio"].value_counts().head(10))

# ---- PASO 9: clasificar cada publicación por lo que dice su contenido ----
def clasificar(contenido):
    if "no requiere gestión" in contenido:
        return "Reconocimiento"
    if contenido.startswith("Compartimos una oportunidad"):
        return "Idea de mejora"
    if contenido.startswith("Para el próximo comité"):
        return "Pedido de información"
    if "se identificó la necesidad" in contenido:
        return "Necesidad"
    if contenido.startswith("Solicitamos revisar"):
        return "Solicitud"
    return "Sin clasificar"


tabla["Intencion"] = tabla["Contenido"].apply(clasificar)

print()
print("PASO 9 - Intención según el contenido")
print(tabla["Intencion"].value_counts())

# Cruce: filas = lo que dice el contenido, columnas = el Tipo que puso el autor
print()
print("Intención (contenido) frente a Tipo (etiqueta del autor):")
print(pd.crosstab(tabla["Intencion"], tabla["Tipo"]))

# ---- PASO 10: marcar accionables y posibles duplicados, y guardar ----
# Accionable: todo lo que no sea un reconocimiento
tabla["Accionable"] = tabla["Intencion"] != "Reconocimiento"

# La publicación misma avisa que el caso puede estar repetido en otro canal
tabla["AvisaDuplicidad"] = tabla["Contenido"].str.contains("duplicidad")

# Publicación repetida: mismo correo, mismo título y mismo contenido
tabla["Repetida"] = tabla.duplicated(["Correo", "Título", "Contenido"], keep=False)

print()
print("PASO 10 - Resumen del archivo")
print("Publicaciones:", len(tabla))
print("Accionables:", tabla["Accionable"].sum())
print("No accionables:", (~tabla["Accionable"]).sum())
print("Avisan posible duplicidad:", tabla["AvisaDuplicidad"].sum())
print("Repetidas (mismo correo, título y contenido):", tabla["Repetida"].sum())

# Se guarda la tabla limpia; utf-8-sig hace que Excel muestre bien las tildes
tabla.drop(columns="Inicio").to_csv(
    "Comunidad_limpia.csv", index=False, encoding="utf-8-sig"
)
print("Archivo guardado: Comunidad_limpia.csv")