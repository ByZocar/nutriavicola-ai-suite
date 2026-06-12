# Nutriavicola AI Suite

Proyecto agéntico, analítico y profesional desarrollado para la prueba técnica de
Analista de Inteligencia Artificial en Nutriavicola. Combina la creación de agentes y
workflows en **Microsoft Copilot Studio** (núcleo de la prueba) con un **extra unificado
en Python**: una plataforma ejecutable y desplegable que demuestra ingeniería de datos e
IA por encima de lo solicitado.

> Este README se construyó en paralelo al desarrollo, fase a fase, documentando QUÉ se
> hizo y POR QUÉ se decidió así.

---

## Tabla de contenidos

- [Qué resuelve](#qué-resuelve)
- [Arquitectura](#arquitectura)
- [Seguridad (defensa en profundidad)](#seguridad-defensa-en-profundidad)
- [Canales de despliegue](#canales-de-despliegue)
- [El extra unificado](#el-extra-unificado)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Cómo ejecutar](#cómo-ejecutar)
- [Decisiones de diseño](#decisiones-de-diseño)
- [Retos de la prueba](#retos-de-la-prueba)

## Qué resuelve

Nutriavicola necesita automatizar la atención de solicitudes internas repetitivas. La
suite cubre dos procesos y los unifica en un solo canal:

- **Recursos Humanos:** generación de certificados laborales bajo demanda.
- **Soporte TI:** consulta del estado de tickets críticos pendientes.

## Arquitectura

Arquitectura general

- Un **orquestador** en Copilot Studio recibe al usuario, lo saluda y reconoce la intención.
- Según la intención, enruta al **sub-flujo de Certificados (RRHH)** o al de **Soporte TI**.
- Los agentes invocan una **API en Python** (el extra) como acción externa, protegida con API key.
- La **seguridad es transversal**: identidad de Entra ID, validación de pertenencia del
documento, enlaces firmados que caducan y contención de errores.

Diagramas disponibles (PDF exportado en `diagramas/`):
[arquitectura general](diagramas/arquitectura_general.pdf),
[arquitectura de seguridad](diagramas/arquitectura_seguridad.pdf),
[flujo del orquestador](diagramas/flujo_orquestador.pdf),
[flujo de certificados](diagramas/flujo_certificados.pdf),
[flujo de soporte TI](diagramas/flujo_soporte_ti.pdf) y
[flujo de datos del extra](diagramas/flujo_datos_extra.pdf).

## Seguridad (defensa en profundidad)

Arquitectura de seguridad

El certificado laboral es un documento con datos personales, así que el diseño asume que
cualquier punto puede fallar o ser atacado y protege en varias capas independientes:

1. **Identidad (Entra ID):** inicio de sesión obligatorio. El correo del usuario autenticado
  viaja al backend como prueba de identidad (`System.User.PrincipalName`).
2. **Validación de pertenencia:** la API verifica que el documento solicitado pertenezca al
  correo autenticado. Nadie puede pedir el certificado de otra persona
   (`generador.validar_identidad`).
3. **API key (`X-API-Key`):** solo Copilot Studio/Power Automate con la clave pueden invocar
  la API. Una petición de internet sin clave recibe `401` (`api/seguridad.py`).
4. **Enlace de descarga firmado:** el PDF se entrega con un token HMAC que caduca (15 min).
  El documento viaja dentro del token, no en la URL: el enlace no es adivinable.
5. **Privacidad del dato (PII):** dataset sintético sin datos reales; los secretos viven en
  variables de entorno, nunca en el repositorio.
6. **Contención conversacional:** los errores técnicos no se filtran al usuario; hay
  moderación de contenido, tres reintentos y escalamiento a un humano ante abuso o fallo.

## Canales de despliegue

El mismo agente de Copilot Studio se publica en varios canales del ecosistema Microsoft 365
de Nutriavícola. Vistas previas del despliegue (HTML → PDF en `diagramas/canales/`):

**Microsoft Teams** — canal principal del personal administrativo; la identidad de Entra ID
fluye automáticamente.

Mockup Teams

**Web (intranet)** — widget embebido vía iframe en el portal del colaborador.

Mockup Web

**WhatsApp** (fase posterior, vía Azure Bot Service) — para el personal de planta y campo que
no usa Teams ni correo corporativo.

Mockup WhatsApp

## El extra unificado

Un solo producto en Python que envuelve capa de datos, API REST, generación de certificado
en PDF, clasificador de tickets, orquestador real y dashboard analítico desplegable.
(Se documenta en detalle al avanzar las fases.)

### Capa de datos (Fase 2)

El módulo `src/nutria_ai/datos/` transforma datos crudos y sensibles en datos confiables
y seguros para ejecutar todo el proyecto. Se decidió así por estas razones:

- **Ingesta (`ingesta.py`):** lee el Excel de empleados y el TXT de tickets (CSV con `;`),
validando que el archivo exista y tolerando distintos encodings (UTF-8 / latin-1).
- **Limpieza (`limpieza.py`):** los datos reales venían sucios. El salario llegaba como
texto (`"$ 3.500.000"`) y se normaliza a número; las fechas se parsean a `datetime`;
el `N/A` de los activos se vuelve nulo real; y los campos vacíos de `Técnico_Asignado`
y `Categoría` se marcan como `Sin asignar` (justo lo que el clasificador completará).
- **Perfilado (`perfilado.py`):** genera un reporte de calidad (filas, nulos, duplicados
y dominios categóricos). Sirve para sustentar decisiones y detectar problemas temprano.
- **Dataset sintético (`sintetico.py`):** genera empleados ficticios con la misma
estructura y dominios realistas, de forma reproducible (semilla fija). Es la pieza que
nos permite ejecutar y publicar el proyecto **sin exponer PII real**.

Para regenerar los artefactos procesados:

```bash
PYTHONPATH=src python -m nutria_ai.datos.pipeline
```

Esto produce en `data/processed/`: `tickets_limpios.csv`, `empleados_sintetico.csv` y los
perfiles de calidad `perfil_tickets.json` y `perfil_empleados.json`.

### Reto 2 - Filtrado de tickets críticos a JSON (Fase 3)

El módulo `src/nutria_ai/tickets/` cumple el Reto 2: lee el archivo de tickets, filtra los
que están `Pendiente` con prioridad `Alta` y genera un JSON consumible por un agente.

- `**filtrado.py`:** aísla la regla de negocio (qué es un ticket crítico). El filtro es
tolerante a mayúsculas/minúsculas y espacios, y valida que existan las columnas
requeridas, lanzando `FormatoTicketsInvalido` con un mensaje claro si faltan.
- `**exportador.py`:** arma el JSON con un campo `total_criticos` explícito (el dato que
el Agente de Soporte TI usará para responder "tienes N tickets críticos") más la lista
de tickets.
- `**cli.py`:** une ingesta -> limpieza -> filtrado -> exportación en un comando, y maneja
los errores esperados (archivo no encontrado, vacío/corrupto, formato inválido)
devolviendo un código de salida en vez de romperse.

Ejecución del Reto 2:

```bash
PYTHONPATH=src python -m nutria_ai.tickets.cli
# o con rutas explícitas:
PYTHONPATH=src python -m nutria_ai.tickets.cli --entrada data/raw/Reto2.txt --salida data/processed/tickets_criticos.json
```

Salida de ejemplo (con los datos de la prueba): **6 tickets críticos**, en
`data/processed/tickets_criticos.json`.

### Extra unificado (Fase 4)

El extra es un solo producto en Python, ejecutable y desplegable, que conecta con los
agentes de Copilot Studio. Cada componente responde a una razón concreta:

- **Certificado en PDF (`certificados/generador.py`):** implementa de verdad la "acción
externa" que el Reto 1 solo pide mencionar. Valida documento + área contra el dataset,
verifica que el documento pertenezca a la identidad autenticada y genera un certificado
laboral formal en PDF, entregado por un enlace firmado que caduca. Si el empleado no existe
o la identidad no coincide, devuelve `exito: false` y el agente lo maneja con reintentos y
escalamiento a un humano.
- **Clasificador (`clasificador/modelo.py`):** los tickets nuevos llegan sin categoría ni
técnico. Un modelo TF-IDF + Naive Bayes sugiere el tipo de incidencia y el nivel de
soporte a partir del título, con su confianza. Es liviano y honesto: el dataset es
pequeño, su valor está en mostrar el flujo de pre-clasificación.
- **Orquestador real (`orquestador/`):** replica en Python la lógica del orquestador de
Copilot Studio. `enrutador.py` reconoce la intención (RRHH vs TI) y `cli.py` es un chat
que saluda, enruta y ejecuta el sub-flujo correcto. Es la prueba viva del Reto 3.
- **API REST (`api/app.py`):** expone como servicio el filtrado, el resumen analítico, el
certificado y el clasificador. Es el punto que Copilot Studio invoca como acción externa.
- **Dashboard (`dashboard/app.py`):** tablero de inteligencia de negocio (carga por
técnico, áreas críticas, prioridades, niveles), contenedorizado y desplegable online.

Ejecución de los componentes:

```bash
# API REST
PYTHONPATH=src uvicorn nutria_ai.api.app:app --reload

# Orquestador por consola
PYTHONPATH=src python -m nutria_ai.orquestador.cli

# Dashboard
PYTHONPATH=src streamlit run src/nutria_ai/dashboard/app.py
```

### Despliegue con Docker y Render

```bash
# Local: levanta API (8000) + dashboard (8501)
docker compose up --build
```

El despliegue online del dashboard usa **Render** (servicio de contenedores): el archivo
`render.yaml` define el servicio web Docker y Render lo construye desde el `Dockerfile`.
Esto deja el tablero accesible por una URL pública para Nutriavicola.

### Integración continua

El workflow `.github/workflows/ci.yml` instala dependencias y corre las pruebas en cada
push y pull request a `main`.

### Pruebas

```bash
PYTHONPATH=src python -m pytest -q
```

Actualmente: **32 pruebas** cubriendo datos, filtrado, certificado, clasificador,
orquestador, API y la capa de seguridad (API key, URLs firmadas y validación de identidad).

### Agentes en Copilot Studio (Fase 5)

El núcleo de la prueba (los agentes y workflows) se construye en **Microsoft Copilot
Studio**. La carpeta `copilot_studio/` deja todo listo para replicarlo y exportarlo:

- `guia_construccion.md`: paso a paso de los tres agentes (frases, nodos, mensajes,
acción externa y fallback).
- `topics/agente_certificados.yaml` y `topics/agente_soporte_ti.yaml`: el "contrato"
estructurado de cada Topic (Retos 1 y 2).
- `orquestador.yaml`: el contrato del agente unificado (Reto 3).
- `acciones/`: las specs HTTP de las acciones externas que conectan los agentes con la
API del extra (`POST /certificados` y `GET /tickets/criticos`).

#### Reto 3 - Ventajas de la arquitectura unificada (orquestador -> sub-flujos)

Tener un único orquestador que enruta hacia sub-flujos, en vez de bots separados, es
superior por varias razones. **Para el usuario** hay un solo canal y una sola identidad:
no tiene que saber a qué bot escribirle, simplemente pide lo que necesita y el motor de
intenciones lo lleva al flujo correcto. **Para el negocio** se centraliza el saludo, el
fallback y la analítica de uso en un solo lugar, y se evita duplicar configuración común.
**Para el mantenimiento** cada capacidad (Certificados, Tickets) queda aislada en su propio
Topic, de modo que se puede mejorar o agregar nuevas capacidades sin tocar las demás: el
orquestador escala agregando sub-flujos, no multiplicando bots que el usuario tendría que
recordar. En resumen, la arquitectura unificada da mejor experiencia, menor costo de
operación y mayor capacidad de crecer de forma ordenada.

### Diagramas (Fase 6)

Siguiendo la regla del proyecto (nada de diagramas en markdown puro), los diagramas se
construyen en HTML con una hoja de estilo común (`diagramas/estilo.css`) y se exportan a
PDF reproducible con WeasyPrint. Para regenerarlos:

```bash
python diagramas/convertir_a_pdf.py
```

Esto produce cinco PDF en `diagramas/`: arquitectura general, flujo del orquestador, flujo
de certificados, flujo de soporte TI y flujo de datos del extra.

## Estructura del repositorio

```
src/nutria_ai/      # código del extra (datos, tickets, certificados, clasificador, api, orquestador, dashboard)
  api/seguridad.py  # API key + URLs firmadas (capa de seguridad)
data/               # raw (ignorado) y processed (versionable, sintético)
tests/              # pruebas con pytest (32)
diagramas/          # HTML fuente + PDF exportados
  canales/          # mockups de despliegue (Teams, Web, WhatsApp)
  img/              # PNG embebidos en este README
copilot_studio/     # exportes y documentación de los agentes
presentacion/       # guion de sustentación
.github/workflows/  # integración continua + keep-alive
```

## Cómo ejecutar

Requisitos: Python 3.12+ y, para los diagramas, las librerías de sistema de WeasyPrint
(pango, cairo). Para el dashboard en contenedor, Docker.

```bash
# 1. Entorno e instalación
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 2. Ubicar los datos crudos en data/raw/ (no se versionan: contienen PII)
#    - data/raw/Reto2.txt        (tickets)
#    - data/raw/empleados.xlsx   (empleados)

# 3. Generar los artefactos procesados (limpios + sintéticos)
PYTHONPATH=src python -m nutria_ai.datos.pipeline

# 4. Reto 2: generar el JSON de tickets críticos
PYTHONPATH=src python -m nutria_ai.tickets.cli

# 5. Probar el orquestador por consola
PYTHONPATH=src python -m nutria_ai.orquestador.cli

# 6. Levantar API + dashboard (opcional, con Docker)
docker compose up --build

# 7. Correr las pruebas
PYTHONPATH=src python -m pytest -q
```

## Decisiones de diseño

- **PII fuera del repositorio:** los datos de empleados contienen documentos y salarios.
No se suben datos reales; se trabaja con un dataset sintético anonimizado de la misma
estructura. Es una decisión de seguridad y privacidad, no una limitación técnica.
- **Diagramas en HTML -> PDF**, no en markdown puro, para que sean profesionales y
reproducibles.
- **Control de versiones granular:** commits pequeños por sub-paso lógico, con historial
legible que cuenta la evolución del desarrollo.
- **Seguridad por capas:** el dato sensible (certificado) se protege con identidad, API key,
enlaces firmados y privacidad de datos. Ver la sección [Seguridad](#seguridad-defensa-en-profundidad).

## Retos de la prueba

- **Reto 1 - Agente de certificados (RRHH):** diseño en Copilot Studio
(`copilot_studio/topics/agente_certificados.yaml` + guía) con frases desencadenantes,
validación de documento + área, acción externa y fallback. La acción externa está
implementada de verdad en el extra (`certificados/generador.py` + API).
- **Reto 2 - Tickets a JSON + agente TI:** script Python que filtra `Pendiente` + `Alta`
y genera el JSON (`tickets/`), más el agente de Soporte TI
(`copilot_studio/topics/agente_soporte_ti.yaml`) que consume el conteo.
- **Reto 3 - Orquestador unificado:** `copilot_studio/orquestador.yaml` y la prueba viva
en Python (`orquestador/`), con el párrafo de ventajas en la sección de Copilot Studio.
- **Reto 4 - Control de versiones y documentación:** historial de commits granular por
sub-paso y este README.

### Extra entregado (por encima de lo pedido)

API REST, generación real del certificado en PDF, clasificador de tickets nuevos,
orquestador ejecutable, dashboard analítico contenedorizado y desplegable en Render,
módulo de calidad de datos con dataset sintético (cero PII), una **capa de seguridad de
nivel producción** (autenticación por API key, validación de identidad contra Entra ID y
enlaces de descarga firmados con caducidad), estrategia **multicanal** (Teams, Web, WhatsApp)
con vistas previas, pruebas (pytest) y CI.