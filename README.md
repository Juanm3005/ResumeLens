# ResumeLens

ResumeLens es un proyecto académico para procesar hojas de vida escritas como texto y comprobar si sus cualificaciones explícitas corresponden con patrones definidos para perfiles profesionales. El proyecto aplica modelos de lenguajes formales para que cada etapa tenga una función delimitada y resultados verificables.

ResumeLens **no ordena candidatos, no recomienda contrataciones y no toma decisiones de empleo**. Solo procesa información escrita en el CV y evalúa patrones previamente definidos.

## Contexto y objetivo del proyecto

Las hojas de vida presentan la misma cualificación de varias maneras: por ejemplo, `JavaScript`, `Javascript` y `JS`; o `Scikit-learn`, `sklearn` y `scikit learn`. También organizan sus estudios, experiencia y habilidades con formatos diferentes. ResumeLens busca extraer esas menciones, normalizar sus variantes, compararlas con perfiles profesionales y validar una representación estructurada de los resultados.

El sistema debe procesar cuatro perfiles usando una misma solución:

1. **Full Stack Developer**, perfil de referencia de ingeniería de software.
2. **Machine Learning Engineer**, perfil de referencia de IA y datos.
3. Un perfil adicional de ingeniería de software definido por el equipo.
4. Un perfil adicional de IA o datos definido por el equipo.

Los dos perfiles adicionales y sus patrones deben acordarse y documentarse por el equipo. La implementación actual no pretende representar todavía los cuatro perfiles.

## Flujo general del sistema

El proyecto completo se organiza en estas etapas:

| Etapa | Modelo | Propósito | Estado en este repositorio |
| --- | --- | --- | --- |
| 1. Extracción | Expresiones regulares con `re` de Python | Detectar texto de contacto, cualificaciones, formación y experiencia, conservando las menciones originales. | Implementada y probada. |
| 2. Normalización | Transductores finitos con `pyformlang` | Convertir variantes explícitas de cualificaciones a nombres canónicos. | Solo hay una vista previa pequeña para probar el flujo desde la extracción. |
| 3. Reconocimiento de perfiles | Autómatas finitos con `pyformlang` | Comprobar si el conjunto ordenado de cualificaciones satisface un patrón de perfil. | Pendiente. |
| 4. Estructuración | Gramática libre de contexto y `textX` | Validar una representación DSL de la información y del resultado de perfil. | Pendiente. |
| 5. Visualización | HTML o Markdown | Presentar la información estructurada validada. | Pendiente. |

La salida de cada etapa alimenta la siguiente. El flujo principal del repositorio hoy es **texto UTF-8 → extracción → estructura de menciones en JSON**; la vista previa opcional muestra cómo una mención extraída puede pasar a una primera normalización.

## Estado y alcance de esta entrega

El foco de esta entrega es el **punto 1: extracción con expresiones regulares**. Se implementan la API Python, el comando de consola, documentación de los patrones y pruebas automatizadas. El punto 2 aparece solo como una demostración de `JS`, `Javascript` y `JavaScript` → `JAVASCRIPT`; no es la normalización completa requerida para el proyecto.

La extracción conserva literalmente lo escrito. Por ejemplo, `JS` sigue siendo `JS` en los resultados del punto 1; el alias se convierte únicamente cuando se ejecuta la vista previa separada del punto 2. El extractor no infiere equivalencias ni reconoce perfiles.

## Desarrollo del punto 1: extracción

### Objetivo y entradas

El extractor recibe una cadena Python con el contenido de una hoja de vida. La interfaz de consola lee archivos de texto plano UTF-8 (`.txt`). Convertir PDF, DOCX o imágenes a texto no forma parte de esta etapa.

La consigna indica que cada tipo de información relevante debe tener una expresión regular definida, una explicación del patrón que reconoce, una implementación con el módulo `re` y un lugar donde guardar los resultados. Esta implementación cumple esos aspectos con el catálogo en [`src/resumelens/patterns.py`](src/resumelens/patterns.py), la ejecución en [`src/resumelens/extraction.py`](src/resumelens/extraction.py) y el modelo `ExtractionResult`. El detalle de cada regex, el lenguaje que reconoce y sus límites está en [docs/stage-1-extraction.md](docs/stage-1-extraction.md).

### Información detectada

| Tipo | Ejemplos de texto reconocido | Representación de salida |
| --- | --- | --- |
| Correos | `alex@example.com`, `Jane.Doe+work@Example.org` | `contacts.emails` |
| Teléfonos | `+57 300 123 4567`, `2025550142` | `contacts.phones`; se filtran fechas numéricas comunes. |
| Enlaces | URLs que empiezan por `http://`, `https://` o `www.` | `contacts.linkedin`, `contacts.github` o `contacts.websites`, según el host. |
| Lenguajes de programación | `JavaScript`, `JS`, `TypeScript`, `Python`, `C++`, `SQL` | `skills.programming_languages` |
| Frameworks y librerías | `React.js`, `NodeJS`, `Django`, `Pandas`, `sklearn`, `TensorFlow`, `PyTorch` | `skills.frameworks_libraries` |
| Bases de datos | `Postgres`, `PostgreSQL`, `MySQL`, `MongoDB`, `SQL Server` | `skills.databases` |
| Herramientas y tecnologías | `Git`, `Docker`, `Kubernetes`, `REST API`, `AWS`, `Linux` | `skills.tools_and_technologies` |
| Otras cualificaciones de los perfiles de referencia | `web applications`, `backend services`, `predictive models`, `data-processing pipelines`, `Machine-learning model development` | `other_qualifications`, agrupadas por tema. |
| Formación académica | `Bachelor of Science`, `B.Sc.`, `Master's degree`, `PhD` | `academic_degrees` |
| Duración de experiencia | `3 years of experience`, `Experience: 2.5 years`, `4+ yrs professional experience` | `experience` |
| Bloque de experiencia | Texto bajo `Experience`, `Work Experience` o `Professional Experience` | `experience_sections`, hasta el siguiente encabezado reconocido. |

El catálogo es explícito y acotado: no detecta automáticamente cualquier tecnología o frase nueva. Para ampliar la cobertura se agrega una alternativa al patrón apropiado, se explica qué texto reconoce y se añade un caso de prueba.

### Cómo se ejecutan los patrones

1. `patterns.py` define cada patrón y, para las categorías de habilidades, su grupo y descripción mediante `PatternDefinition`.
2. `extract_resume(text)` valida la entrada y aplica los patrones con `re.finditer`, normalmente con `re.IGNORECASE`. Las expresiones de encabezado usan los indicadores inline `(?im)` para búsqueda multilínea sin distinguir mayúsculas.
3. Cada coincidencia se guarda como `ExtractionMatch(value, start, end)`. `value` copia exactamente el fragmento original; `start` y `end` son offsets Python y el extremo `end` no se incluye.
4. Las URLs se clasifican por host y se les quita la puntuación final de oración. Los candidatos a teléfono con forma de fecha común se descartan.
5. Las duraciones de experiencia se extraen con regex; los bloques de experiencia se capturan entre un encabezado laboral y el siguiente encabezado común del CV.
6. El resultado se agrupa en `ExtractionResult`, con categorías vacías estables, y se puede serializar con `to_dict()` o `to_json()`.

Las coincidencias no se canonicalizan ni se usan para evaluar perfiles en esta etapa. Por ejemplo, que aparezca `Python` en un CV no implica que la persona tenga determinado nivel de dominio.

### Forma del resultado

Cada mención contiene su texto y los offsets que permiten recuperarla de la entrada. Simplificado, el JSON incluye:

```json
{
  "contacts": {
    "emails": [{"value": "alex@example.com", "start": 7, "end": 23}],
    "phones": [],
    "linkedin": [],
    "github": [],
    "websites": []
  },
  "skills": {
    "programming_languages": [{"value": "JS", "start": 31, "end": 33}],
    "frameworks_libraries": [],
    "databases": [],
    "tools_and_technologies": []
  },
  "other_qualifications": {
    "software_development": [],
    "machine_learning": [],
    "data_processing": []
  },
  "academic_degrees": [],
  "experience": [],
  "experience_sections": []
}
```

Los índices del ejemplo son ilustrativos; para cada entrada real se calculan desde la cadena fuente. La documentación ampliada incluye las expresiones completas y sus reglas de reconocimiento.

### Limitaciones conocidas

- La CLI acepta texto plano UTF-8; no extrae texto de PDF, DOCX ni imágenes.
- El catálogo cubre vocabulario explícito. Una tecnología, abreviatura o descripción que no esté contemplada no se extraerá.
- Los nombres de títulos, duraciones y encabezados se orientan principalmente a CV en inglés; se pueden agregar variantes en otros idiomas.
- La identificación de teléfonos es por forma y no valida números contra un plan telefónico nacional.
- El bloque de experiencia depende de encabezados reconocidos en una línea propia; otro formato puede requerir ampliar el catálogo de encabezados.
- Las coincidencias explícitas no son prueba de dominio ni una recomendación de contratación.

## Instalación y uso

Se recomienda un entorno virtual para aislar las dependencias de este proyecto. Requiere Python 3.10 o posterior.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

En macOS o Linux, el comando de activación es `source .venv/bin/activate`; los demás comandos son iguales. Si la política de PowerShell impide activar el entorno, usa directamente `.\.venv\Scripts\python.exe` en lugar de `python` en los comandos.

Con el entorno activo, guarda el CV de texto como `resume.txt` y ejecuta:

```powershell
python -m resumelens .\resume.txt
```

Para guardar el JSON en un archivo:

```powershell
python -m resumelens .\resume.txt --output .\extraction.json
```

También se puede usar `-o` en lugar de `--output`. La API está disponible desde Python:

```python
from resumelens import extract_resume

result = extract_resume("Skills: JS, React.js, NodeJS, Postgres, Git.")
print(result.to_json())
```

## Pruebas y verificación

Con `.venv` activo, ejecuta la suite completa:

```powershell
python -m unittest discover -s tests -v
```

El dataset [`tests/fixtures/stage1_extraction_dataset.json`](tests/fixtures/stage1_extraction_dataset.json) contiene **94 casos de regresión** con IDs únicos. La suite cubre los ejemplos de Full Stack y Machine Learning de la consigna, categorías y variantes, límites para evitar coincidencias parciales, datos de contacto, offsets Unicode, serialización JSON y salidas de consola y archivo. Si también instalas el extra opcional del punto 2, la prueba de integración del transductor se ejecuta en vez de omitirse.

## Dependencias por etapa

- Punto 1: no usa paquetes externos en tiempo de ejecución.
- Instalación del paquete: `setuptools`, declarado como backend de construcción en `pyproject.toml`.
- Vista previa del punto 2: `pyformlang` y sus dependencias, declarados como extra opcional `stage2-preview`.

Para activar y probar la vista previa del transductor:

```powershell
python -m pip install -e ".[stage2-preview]"
python -m unittest discover -s tests -p "test_normalization_preview.py" -v
```

La demostración solo transforma `JS`, `Javascript` y `JavaScript` en `JAVASCRIPT`. Su modelo y alcance están descritos en [docs/stage-2-normalization-preview.md](docs/stage-2-normalization-preview.md). La API de `pyformlang` y la documentación del proyecto se mantienen como referencias para completar después el punto 2.

## Estructura del repositorio

```text
src/resumelens/
  __init__.py                  API pública
  __main__.py                  Entrada para python -m resumelens
  cli.py                       Lectura de texto y salida JSON
  extraction.py                Extracción y estructuras de resultados
  normalization_preview.py     Demostración opcional del punto 2
  patterns.py                  Catálogo de expresiones regulares
pyproject.toml                 Configuración de instalación
tests/
  test_cli.py
  test_extraction.py
  test_normalization_preview.py
  test_stage1_dataset.py
  fixtures/stage1_extraction_dataset.json
docs/
  stage-1-extraction.md
  stage-2-normalization-preview.md
```

## Próximos pasos para el equipo

1. Completar el punto 2 con transductores que normalicen las variantes acordadas por el equipo. Para cada uno, documentar el 7-tuplo, el diagrama y pruebas con entradas y salidas esperadas.
2. Definir los cuatro perfiles —incluidos los dos adicionales del equipo— y reconocer sus patrones mediante autómatas finitos.
3. Diseñar la gramática EBNF del perfil estructurado, implementarla con `textX` y probar que acepte entradas válidas y rechace las inválidas.
4. Generar la visualización Markdown o HTML desde el perfil estructurado validado.

La vista previa del punto 2 sirve para demostrar el encadenamiento, pero no reemplaza el diseño y la implementación que faltan en esas etapas.
