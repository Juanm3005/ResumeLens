# Punto 1 — Extracción con expresiones regulares

## Objetivo y límites

Esta etapa encuentra fragmentos relevantes de una hoja de vida en texto plano usando `re` de Python. El dominio de entrada son menciones literales: cualificaciones, datos de contacto, estudios y experiencia. Incluye un catálogo acotado de frases adicionales que aparecen en los perfiles de referencia, como desarrollo de aplicaciones web, modelos predictivos y pipelines de procesamiento de datos. No se infiere información que no esté escrita. No se decide si dos menciones son equivalentes, no se normalizan alias y no se reconoce ningún perfil.

La unidad de salida es una coincidencia `(value, start, end)`. `value` es una porción exacta del texto fuente y `start`/`end` son offsets Python con el límite final excluido. Los offsets mantienen trazabilidad, incluso cuando la entrada contiene caracteres Unicode. Para experiencia profesional se guardan tanto frases de duración detectadas como el contenido literal bajo encabezados laborales comunes; esto conserva el cargo y sus descripciones para las siguientes etapas.

## Catálogo de patrones

Todos los patrones de tecnologías, formación y experiencia se ejecutan con `re.IGNORECASE`. El contenido de cada coincidencia conserva el uso de mayúsculas/minúsculas del CV.

### Contacto

| Campo | Expresión o regla | Patrón reconocido |
| --- | --- | --- |
| Correo | `(?<![\w.+-])[\w.!#$%&'*+/=?^_{}|~-]+@[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?(?:\.[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?)+` | Una parte local con caracteres habituales, `@` y un dominio de al menos dos etiquetas separadas por puntos. |
| Teléfono | `(?<!\w)(?:\+\d{1,3}[ .-]?)?(?:\(?\d{2,4}\)?[ .-])?\d{3,4}[ .-]\d{3,4}(?!\w)` o `(?<!\w)\+?\d{10,15}(?!\w)` | Número con prefijo internacional opcional y grupos separados, o número continuo de 10–15 dígitos. Una validación posterior excluye fechas comunes `AAAA-MM-DD`, `AAAA/MM/DD` y `AAAA.MM.DD`. |
| URL | `(?i)\b(?:https?://|www\.)[^\s<>()]+` | URL que comienza por `http://`, `https://` o `www.` y continúa hasta un espacio o delimitador. Se quita puntuación final de oración; un host igual a `linkedin.com`/`github.com` o un subdominio suyo se clasifica como tal. Dominios parecidos, como `notlinkedin.com`, quedan como sitios web. |

### Cualificaciones

Las regex se agrupan en `SKILL_PATTERNS` en `src/resumelens/patterns.py`. Las alternativas reconocen vocabularios explícitos y se guardan como aparecen.

| Categoría | Expresión regular | Ejemplos de coincidencias |
| --- | --- | --- |
| `programming_languages` | `(?<![\w+#.])(?:JavaScript|Javascript|JS|TypeScript|Java|C\+\+|C#|Python|Ruby|PHP|Kotlin|Swift|Rust|SQL)(?![\w+#])` | `JS`, `Javascript`, `Python`, `SQL`, `C++` |
| `frameworks_libraries` | `(?<![\w.])(?:React(?:\.js|JS)?|Angular|Vue(?:\.js)?|Node(?:\.js|JS)|Django|Spring\s+Boot|Flask|FastAPI|Express(?:\.js)?|Pandas|NumPy|Scikit[- ]learn|scikit\s+learn|sklearn|Tensor\s*Flow|Py\s*Torch)(?!\w|\.(?:js))` | `React.js`, `ReactJS`, `NodeJS`, `scikit learn`, `sklearn`, `Tensor Flow`, `Py Torch` |
| `databases` | `(?<![\w.])(?:PostgreSQL|Postgres|MySQL|SQLite|MongoDB|Redis|Oracle|SQL\s+Server)(?!\w)` | `Postgres`, `PostgreSQL`, `MongoDB`, `SQL Server` |
| `tools_and_technologies` | `(?<![\w.])(?:Git|Docker|Kubernetes|REST(?:ful)?\s+APIs?|AWS|Azure|GCP|Linux)(?!\w)` | `Git`, `Docker`, `REST API`, `RESTful APIs`, `AWS` |

### Otras cualificaciones de los perfiles de referencia

Las siguientes regex acotadas detectan frases de experiencia y cualificación incluidas en los perfiles Full Stack y Machine Learning de la consigna. Se agrupan en `other_qualifications` para mantenerlas separadas de nombres de tecnologías:

| Grupo | Expresión regular | Ejemplos |
| --- | --- | --- |
| `software_development` | `(?<!\w)(?:web\s+applications?|backend\s+services?)(?!\w)` | `web applications`, `backend services` |
| `machine_learning` | `(?<!\w)(?:machine[- ]learning\s+model\s+development|predictive\s+models?)(?!\w)` | `Machine-learning model development`, `predictive models` |
| `data_processing` | `(?<!\w)data[- ]processing\s+pipelines?(?!\w)` | `data-processing pipelines`, `Data processing pipeline` |

El catálogo se limita a frases escritas explícitamente y puede crecer agregando patrones y casos de prueba. No clasifica al candidato.

Los límites con lookbehind/lookahead (`(?<!...)`, `(?!...)`) previenen coincidencias dentro de palabras mayores. Las alternativas (`|`) aceptan varios nombres; `?` hace opcional una parte; `\s` acepta espacios en blanco. Un catálogo acotado evita aceptar como tecnología cualquier palabra arbitraria. Se puede ampliar agregando alternativas a la categoría adecuada y casos a `tests/test_extraction.py`.

### Formación académica

Expresión aplicada:

```regex
(?<!\w)(?:Bachelor(?:'s)?(?:\s+(?:degree|of\s+(?:Science|Arts|Engineering)))?|B\.?\s?Sc\.?|B\.?\s?A\.?|B\.?\s?Eng\.?|Master(?:'s)?(?:\s+(?:degree|of\s+(?:Science|Arts|Engineering)))?|M\.?\s?Sc\.?|M\.?\s?A\.?|M\.?\s?Eng\.?|Ph\.?\s?D\.?|doctorate|associate(?:'s)?(?:\s+degree)?)(?!\w)
```

Reconoce nombres y abreviaturas frecuentes para títulos de pregrado, maestría, doctorado y associate degree, por ejemplo `Bachelor of Science`, `M.Sc.` y `PhD`. No extrae universidades, especialidades ni fechas. El vocabulario actual está orientado a menciones en inglés.

### Experiencia profesional

Se usan dos patrones para admitir ambos órdenes:

```regex
(?<!\w)\d+(?:\.\d+)?\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+)?experience(?!\w)
(?<!\w)experience\s*(?:of|:)?\s*\d+(?:\.\d+)?\s*\+?\s*(?:years?|yrs?)(?!\w)
```

Reconocen una cantidad entera o decimal de años, con `+` opcional, y el término `year`/`years` o `yr`/`yrs` relacionado con `experience`. Por ejemplo: `3 years of experience`, `3 yrs professional experience` y `Experience: 2.5 years`. No calculan fechas ni convierten meses a años.

Además, para conservar el cargo y sus descripciones, se captura el bloque bajo un encabezado laboral. La regex de inicio es:

```regex
(?im)^[ \t]*(?:(?:professional|work)[ \t]+)?experience(?:[ \t]+history)?[ \t]*:?[ \t]*(?:\r?\n|$)
```

Reconoce, al comienzo de una línea y sin distinguir mayúsculas, `Experience`, `Work Experience`, `Professional Experience` y la variante con `History`, opcionalmente seguidas de dos puntos. El bloque termina antes de la siguiente línea que coincida con la regex de encabezados de sección:

```regex
(?im)^[ \t]*(?:education|academic(?:[ \t]+background)?|technical[ \t]+skills|skills|projects?|certifications?|contact(?:[ \t]+information)?|summary|profile|languages?|publications?|awards?|references?|training)[ \t]*:?[ \t]*(?:\r?\n|$)
```

Esta regex reconoce encabezados habituales como `Education`, `Technical Skills`, `Projects` y `Certifications`. `re.finditer` localiza el inicio y `re.search` encuentra el siguiente encabezado; el contenido entre ambos se conserva como `experience_sections` con offsets al texto original. Los encabezados deben ocupar una línea propia para que la delimitación sea inequívoca.

## Estructura de salida

`extract_resume(text)` retorna un `ExtractionResult`. `to_dict()`/`to_json()` producen estas claves:

- `contacts`: `emails`, `phones`, `linkedin`, `github`, `websites`.
- `skills`: `programming_languages`, `frameworks_libraries`, `databases`, `tools_and_technologies`.
- `other_qualifications`: `software_development`, `machine_learning`, `data_processing`.
- `academic_degrees` y `experience`.
- `experience_sections`, con el texto bajo encabezados como `Experience`, `Work Experience` o `Professional Experience`, hasta el siguiente encabezado común detectado.

Cada elemento es un objeto con `value`, `start` y `end`. Las categorías sin resultados se incluyen con listas vacías para mantener una estructura estable.

## Ejecución y verificación

Instala el paquete en modo editable desde la raíz del repositorio:

```powershell
python -m pip install -e .
```

La interfaz de consola lee un archivo `.txt` UTF-8 e imprime JSON; también permite escribirlo con `--output`:

```powershell
python -m resumelens .\resume.txt --output .\extraction.json
python -m unittest discover -s tests -v
```

Las pruebas comprueban ejemplos de cualificaciones de la consigna, variantes literales, correo/teléfono/URLs, filtro de fechas, grados, experiencia, cualificaciones en prosa, offsets, JSON y ambos destinos de la CLI. Además, `tests/fixtures/stage1_extraction_dataset.json` contiene **94 casos de regresión**. Cada registro incluye un identificador, texto de entrada y resultados esperados; las claves omitidas deben quedar vacías. `tests/test_stage1_dataset.py` convierte cada registro en una prueba individual, valida todas las categorías y verifica que cada offset recupere el fragmento literal.

## Limitaciones conocidas

- Solo se lee texto plano UTF-8; no hay extracción de texto desde PDF, DOCX o imágenes.
- La cobertura depende del vocabulario de patrones: una tecnología no incluida no se detectará.
- Los títulos académicos y expresiones de experiencia reconocen vocabulario en inglés; los CV en español necesitan patrones adicionales.
- La extracción por bloque depende de encabezados de sección comunes en inglés. Un formato distinto puede no delimitar el bloque y requiere agregar encabezados reconocidos.
- Los teléfonos se detectan por forma y no se validan contra un plan nacional. El filtro evita formatos de fecha comunes, pero no garantiza que cualquier número restante sea un teléfono.
- Las menciones extraídas no son evidencia de dominio ni se usan para recomendar, clasificar o descartar candidatos.
