# ResumeLens

ResumeLens procesa hojas de vida para identificar cualificaciones explícitas con modelos de lenguajes formales. El alcance principal de este repositorio es el **punto 1: extracción mediante expresiones regulares**. Se incluye además una vista previa mínima y opcional del punto 2 para comprobar el flujo entre etapas.

## Alcance de esta etapa

El extractor usa el módulo estándar `re` de Python para detectar:

| Grupo | Información detectada |
| --- | --- |
| Contacto | Correos, teléfonos y enlaces de LinkedIn, GitHub y otros sitios |
| Lenguajes | Lenguajes de programación y SQL |
| Frameworks y librerías | React, Node.js, Django, Pandas, scikit-learn, TensorFlow, entre otros |
| Bases de datos | PostgreSQL, MySQL, MongoDB, SQLite, entre otras |
| Herramientas y tecnologías | Git, Docker, Kubernetes, servicios cloud, REST API y Linux |
| Formación | Nombres frecuentes de títulos académicos y abreviaturas |
| Otras cualificaciones | Frases explícitas del perfil, como desarrollo de aplicaciones web, modelos predictivos y pipelines de procesamiento de datos |
| Experiencia | Cantidades expresadas en años o `yrs` junto con `experience`, y texto literal bajo encabezados comunes de experiencia laboral |

Cada resultado conserva el texto literal que coincidió y sus posiciones `start`/`end` en la entrada. Así, `JS`, `Javascript` y `JavaScript` siguen siendo menciones diferentes: **esta etapa no normaliza equivalencias, no clasifica perfiles y no toma decisiones sobre candidatos**. El catálogo de expresiones y los lenguajes que reconoce están descritos en [docs/stage-1-extraction.md](docs/stage-1-extraction.md).

## Requisitos

- Python 3.10 o posterior.
- No se requieren paquetes externos durante la ejecución de la extracción.
- Para instalar el paquete en modo editable y habilitar `python -m resumelens`: `python -m pip install -e .` (usa setuptools como backend de construcción).
- La vista previa opcional del punto 2 requiere `pyformlang`, que se instala con `python -m pip install -e ".[stage2-preview]"`.
- Entrada en texto plano UTF-8 (`.txt`). La conversión de PDF/DOCX a texto no forma parte de esta etapa.

## Uso

Desde la carpeta raíz del repositorio, guarda el texto de una hoja de vida como `resume.txt` y ejecuta:

```powershell
python -m pip install -e .
python -m resumelens .\resume.txt
```

El resultado JSON se imprime en la consola. Para guardarlo en un archivo:

```powershell
python -m resumelens .\resume.txt --output .\extraction.json
```

También se puede usar la forma corta `-o`. El JSON agrupa los resultados por categoría e incluye el fragmento encontrado y los offsets; las categorías sin coincidencias aparecen como listas vacías. `experience_sections` conserva el contenido bajo encabezados como `Professional Experience` hasta el siguiente encabezado común del CV.

La función Python está disponible directamente:

```python
from resumelens import extract_resume

result = extract_resume("Skills: JS, React.js, NodeJS, Postgres, Git.")
print(result.to_json())
```

## Ejemplo

Entrada:

```text
Wednesday Addams
3 years of experience developing web applications.
Technical Skills: JS, React.js, NodeJS, Postgres, Git.
```

Entre los resultados se extraen literalmente `JS`, `React.js`, `NodeJS`, `Postgres` y `Git`, además de `3 years of experience`. Cada mención incluye los índices que permiten recuperarla del texto original. No se transforma `JS` en `JAVASCRIPT` ni se evalúa si la persona satisface un perfil.

## Cómo se resolvió el punto 1

1. Se definió un catálogo de regex por tipo de dato en `src/resumelens/patterns.py`.
2. `src/resumelens/extraction.py` ejecuta esos patrones con `re`, crea coincidencias con texto y offsets, y agrupa los resultados en `ExtractionResult`.
3. Los correos, teléfonos y URLs se extraen por separado de las cualificaciones. Las URLs se agrupan por host como LinkedIn, GitHub o sitio web.
4. Se extraen tanto duraciones explícitas como el bloque de texto de experiencia profesional, conservando el contenido y offsets originales para alimentar etapas posteriores.
5. El resultado se puede serializar a JSON y guardar con la interfaz de consola.
6. Se añadieron pruebas unitarias para los ejemplos de Full Stack y Machine Learning de la consigna, la salida por consola/archivo y un dataset de regresión independiente con **94 casos**. Ese dataset cubre las variantes del catálogo, los datos de contacto, los títulos, frases de cualificaciones por perfil, la experiencia y límites para evitar coincidencias parciales.

Las expresiones son sensibles a los límites de palabra para evitar extraer nombres de tecnología como parte de palabras más largas. Se aplica `re.IGNORECASE`, conservando siempre mayúsculas, minúsculas y puntuación de la coincidencia original. Las decisiones de diseño, el catálogo y sus limitaciones están ampliados en el documento enlazado arriba.

## Ejecutar las pruebas

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
```

`tests/test_normalization_preview.py` omite la prueba de integración si el extra `stage2-preview` no está instalado. La vista previa demuestra únicamente las equivalencias `JS`, `Javascript` y `JavaScript` → `JAVASCRIPT`; está explicada en [docs/stage-2-normalization-preview.md](docs/stage-2-normalization-preview.md).

## Estructura

```text
src/resumelens/
  __init__.py       API pública
  __main__.py       Entrada para python -m resumelens
  cli.py            Lectura de texto y salida JSON
  extraction.py     Ejecución de patrones y modelo de resultados
  normalization_preview.py Demostración opcional del transductor del punto 2
  patterns.py       Catálogo de expresiones regulares
pyproject.toml      Configuración de instalación del paquete
tests/
  test_cli.py
  test_extraction.py
  test_normalization_preview.py
  test_stage1_dataset.py
  fixtures/
    stage1_extraction_dataset.json
docs/
  stage-1-extraction.md
  stage-2-normalization-preview.md
```

## Siguiente paso

Continuar con el **punto 2: normalización de cualificaciones mediante transductores finitos**. La vista previa actual solo transforma `JS`, `Javascript` y `JavaScript` en `JAVASCRIPT`; el siguiente trabajo es ampliar esa idea a las variantes relevantes que entrega el extractor, definir cada transductor con su 7-tupla (`Q`, `Σ`, `Γ`, `δ`, `ω`, `q0`, `F`), dibujar sus transiciones y verificar las salidas con pruebas. Las cualificaciones normalizadas quedarán listas para el punto 3, que reconoce patrones de perfiles con autómatas finitos.

Para ejecutar la vista previa existente instala el extra opcional con `python -m pip install -e ".[stage2-preview]"`. La implementación completa del punto 2 deberá cubrir las transformaciones acordadas por el equipo; la vista previa no las reemplaza.
