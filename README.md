# ResumeLens

ResumeLens procesa hojas de vida para identificar cualificaciones explícitas con modelos de lenguajes formales. Este repositorio implementa **únicamente el punto 1: extracción mediante expresiones regulares**. Las menciones encontradas quedan disponibles para etapas posteriores.

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
| Experiencia | Cantidades expresadas en años o `yrs` junto con la palabra `experience` |

Cada resultado conserva el texto literal que coincidió y sus posiciones `start`/`end` en la entrada. Así, `JS`, `Javascript` y `JavaScript` siguen siendo menciones diferentes: **esta etapa no normaliza equivalencias, no clasifica perfiles y no toma decisiones sobre candidatos**. El catálogo de expresiones y los lenguajes que reconoce están descritos en [docs/stage-1-extraction.md](docs/stage-1-extraction.md).

## Requisitos

- Python 3.10 o posterior.
- No se requieren paquetes externos.
- Entrada en texto plano UTF-8 (`.txt`). La conversión de PDF/DOCX a texto no forma parte de esta etapa.

## Uso

Desde la carpeta raíz del repositorio, guarda el texto de una hoja de vida como `resume.txt` y ejecuta:

```powershell
python -m resumelens .\resume.txt
```

El resultado JSON se imprime en la consola. Para guardarlo en un archivo:

```powershell
python -m resumelens .\resume.txt --output .\extraction.json
```

También se puede usar la forma corta `-o`. El JSON agrupa los resultados por categoría e incluye el fragmento encontrado y los offsets; las categorías sin coincidencias aparecen como listas vacías.

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

1. Se definió un catálogo de regex por tipo de dato en `resumelens/patterns.py`.
2. `resumelens/extraction.py` ejecuta esos patrones con `re`, crea coincidencias con texto y offsets, y agrupa los resultados en `ExtractionResult`.
3. Los correos, teléfonos y URLs se extraen por separado de las cualificaciones. Las URLs se agrupan por host como LinkedIn, GitHub o sitio web.
4. El resultado se puede serializar a JSON y guardar con la interfaz de consola.
5. Se añadieron pruebas unitarias para los ejemplos de Full Stack y Machine Learning de la consigna, las variantes escritas, los datos de contacto, los títulos, la experiencia y la salida por consola/archivo.

Las expresiones son sensibles a los límites de palabra para evitar extraer nombres de tecnología como parte de palabras más largas. Se aplica `re.IGNORECASE`, conservando siempre mayúsculas, minúsculas y puntuación de la coincidencia original. Las decisiones de diseño, el catálogo y sus limitaciones están ampliados en el documento enlazado arriba.

## Ejecutar las pruebas

```powershell
python -m unittest discover -s tests -v
```

## Estructura

```text
resumelens/
  __init__.py       API pública
  __main__.py       Entrada para python -m resumelens
  cli.py            Lectura de texto y salida JSON
  extraction.py     Ejecución de patrones y modelo de resultados
  patterns.py       Catálogo de expresiones regulares
tests/
  test_cli.py
  test_extraction.py
docs/
  stage-1-extraction.md
```
