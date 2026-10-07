# Gestión centralizada de solicitudes · Gerencia de Prestación

Prueba técnica práctica · Analista de Automatización y Transformación de Herramientas
Brian Alexander Filos Salazar · octubre de 2026

MVP en Power Platform para centralizar el registro de solicitudes, calcular el plazo, asignar responsable, escalar lo vencido y dejar trazabilidad de cada cambio, con el análisis de las fuentes entregadas y una alternativa tecnológica.

## Por dónde empezar

1. Abrir `presentacion/index.html` con doble clic. No necesita instalación ni conexión.
2. Avanzar con las flechas del teclado. En las láminas con menú, las flechas recorren primero las pestañas.
3. El video de la demostración está en la lámina 6, pestaña Demo (`presentacion/demo.mp4`).

## Dónde está cada entregable

| Entregable | Dónde verlo |
|---|---|
| 1 · Análisis AS-IS | Presentación, lámina 4: proceso, ficha, problemas, riesgos, cuellos de botella y oportunidades |
| 2 · Diseño TO-BE | Presentación, lámina 5: flujo futuro, actores, reglas, datos, controles e historias de usuario |
| 3 · Power App | Presentación, lámina 6 · `solucion/` · `evidencias/app/` |
| 4 · Automatización | Presentación, lámina 6 (Flujos, Pruebas, Escala y monitoreo) · `solucion/` · `evidencias/flujo/` |
| 5 · Analítica | Presentación, lámina 7 · `datos/Indicadores_Analitica.py` · Vista gerencial de la app |
| 6 · IA | Presentación, lámina 8 (propuesta diseñada, no implementada) |
| 7 · Alternativa | Presentación, lámina 9: arquitectura, comparación, hoja de ruta y recomendación |

## Contenido

| Carpeta | Qué contiene |
|---|---|
| `presentacion/` | `index.html` (la presentación) y el video `demo.mp4` |
| `solucion/` | Solución de Power Platform exportada (no administrada): la app de lienzo, los dos flujos y las tablas |
| `powerapp/carga/` | Archivos cargados a Dataverse: catálogos y solicitudes del histórico ya estandarizadas |
| `datos/` | Fuentes entregadas, un script de análisis por fuente y los archivos limpios que generan |
| `evidencias/` | Capturas de las pruebas del flujo y de las pantallas de la app |

En el repositorio público no están los archivos de datos de `datos/` ni de `powerapp/carga/`: son las fuentes entregadas para la prueba y sus derivados, y solo van en el archivo enviado a los evaluadores. Los scripts y sus resultados sí están, y la presentación muestra el código y la salida de cada paso.

## Lo construido

- **App de lienzo `Solicitudes Prestación`**, con cinco pantallas: Inicio, Registro, Consulta, Detalle y Vista gerencial.
- **Flujo `Solicitudes · Al crear o modificar`**: valida que la información esté completa, calcula el plazo según el catálogo, asigna a la persona activa con la especialidad y con menos carga, avisa por correo, calcula horas y cumplimiento al cerrar y deja un evento por cada paso. Si algo falla, registra el error, avisa y marca la ejecución como fallida.
- **Flujo `Solicitudes · Vigilar plazos`**: cada hora escala las solicitudes abiertas con el plazo vencido, con el nivel que define el catálogo.
- **Cinco tablas en Dataverse**: Solicitudes, Categorías, SLA, Responsables y Eventos.

## Cómo reproducir

**Análisis de las fuentes.** Python 3.12 con `pandas`, `openpyxl` y `python-docx`. Desde la carpeta `datos`:

```
python Catalogos_Gobierno.py
python Historico_Solicitudes.py
python Solicitudes_Correo.py
python Comunidad_Prestacion.py
python Actas_Mesa_Operativa.py
python Indicadores_Analitica.py
```

**Solución.** En un entorno de Power Platform con Dataverse: Soluciones → Importar solución → archivo de `solucion/`. Luego cargar los archivos de `powerapp/carga/` con flujos de datos, uno por tabla. La solución no incluye los datos.

## Alcance y límites

- La app vive en un entorno de desarrollo y solo abre con la cuenta que la construyó. La demostración se hace compartiendo pantalla; el video queda como respaldo.
- No quedó construido: adjuntar evidencia, editar título y descripción, roles de seguridad, alerta previa al vencimiento, detección de duplicados entre canales, tablero en Power BI y la capacidad de IA.
- Los correos `@sura.com.co` del catálogo de responsables son datos simulados; las notificaciones de prueba se enviaron a una dirección propia.
- Las cifras salen de las fuentes entregadas o se declaran como supuestos, como la capacidad diaria nominal.
