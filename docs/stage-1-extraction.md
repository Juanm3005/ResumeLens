# Punto 1 — Extracción con expresiones regulares

## Objetivo y límites

Esta etapa encuentra fragmentos relevantes de una hoja de vida en texto plano usando `re` de Python. El dominio de entrada son menciones literales: cualificaciones, datos de contacto, estudios y duración de experiencia. No se infiere información que no esté escrita. No se decide si dos menciones son equivalentes, no se normalizan alias y no se reconoce ningún perfil.

La unidad de salida es una coincidencia `(value, start, end)`. `value` es una porción exacta del texto fuente y `start`/`end` son offsets Python con el límite final excluido. Los offsets mantienen trazabilidad, incluso cuando la entrada contiene caracteres Unicode.

## Catálogo de patrones

Todos los patrones de tecnologías, formación y experiencia se ejecutan con `re.IGNORECASE`. El contenido de cada coincidencia conserva el uso de mayúsculas/minúsculas del CV.

### Contacto

| Campo | Expresión o regla | Patrón reconocido |
| --- | --- | --- |
| Correo | `(?<![\w.+-])[\w.!#$%&'*+/=?^_{}|~-]+@[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?(?:\.[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?)+` | Una parte local con caracteres habituales, `@` y un dominio de al menos dos etiquetas separadas por puntos. |
| Teléfono | `(?<!\w)(?:\+\d{1,3}[ .-]?)?(?:\(?\d{2,4}\)?[ .-])?\d{3,4}[ .-]\d{3,4}(?!\w)` o `(?<!\w)\+?\d{10,15}(?!\w)` | Número con prefijo internacional opcional y grupos separados, o número continuo de 10–15 dígitos. Una validación posterior excluye fechas comunes `AAAA-MM-DD`, `AAAA/MM/DD` y `AAAA.MM.DD`. |
| URL | `(?i)\b(?:https?://|www\.)[^\s<>()]+` | URL que comienza por `http://`, `https://` o `www.` y continúa hasta un espacio o delimitador. Se quita puntuación final de oración; el host determina si se agrupa como LinkedIn, GitHub o sitio web. |

### Cualificaciones

Las regex se agrupan en `SKILL_PATTERNS` en `resumelens/patterns.py`. Las alternativas reconocen vocabularios explícitos y se guardan como aparecen.

| Categoría | Expresión regular | Ejemplos de coincidencias |
| --- | --- | --- |
| `programming_languages` | `(?<![\w+#.])(?:JavaScript|Javascript|JS|TypeScript|Java|C\+\+|C#|Python|Ruby|PHP|Kotlin|Swift|Rust|SQL)(?![\w+#])` | `JS`, `Javascript`, `Python`, `SQL`, `C++` |
| `frameworks_libraries` | `(?<![\w.])(?:React(?:\.js|JS)?|Angular|Vue(?:\.js)?|Node(?:\.js|JS)|Django|Spring\s+Boot|Flask|FastAPI|Express(?:\.js)?|Pandas|NumPy|Scikit[- ]learn|scikit\s+learn|sklearn|Tensor\s*Flow|Py\s*Torch)(?!\w|\.(?:js))` | `React.js`, `ReactJS`, `NodeJS`, `scikit learn`, `sklearn`, `Tensor Flow`, `Py Torch` |
| `databases` | `(?<![\w.])(?:PostgreSQL|Postgres|MySQL|SQLite|MongoDB|Redis|Oracle|SQL\s+Server)(?!\w)` | `Postgres`, `PostgreSQL`, `MongoDB`, `SQL Server` |
| `tools_and_technologies` | `(?<![\w.])(?:Git|Docker|Kubernetes|REST(?:ful)?\s+APIs?|AWS|Azure|GCP|Linux)(?!\w)` | `Git`, `Docker`, `REST API`, `RESTful APIs`, `AWS` |

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

## Estructura de salida

`extract_resume(text)` retorna un `ExtractionResult`. `to_dict()`/`to_json()` producen estas claves:

- `contacts`: `emails`, `phones`, `linkedin`, `github`, `websites`.
- `skills`: `programming_languages`, `frameworks_libraries`, `databases`, `tools_and_technologies`.
- `academic_degrees` y `experience`.

Cada elemento es un objeto con `value`, `start` y `end`. Las categorías sin resultados se incluyen con listas vacías para mantener una estructura estable.

## Ejecución y verificación

La interfaz de consola lee un archivo `.txt` UTF-8 e imprime JSON; también permite escribirlo con `--output`:

```powershell
python -m resumelens .\resume.txt --output .\extraction.json
python -m unittest discover -s tests -v
```

Las pruebas comprueban ejemplos de cualificaciones de la consigna, variantes literales, correo/teléfono/URLs, filtro de fechas, grados, experiencia, offsets, JSON y ambos destinos de la CLI.

## Limitaciones conocidas

- Solo se lee texto plano UTF-8; no hay extracción de texto desde PDF, DOCX o imágenes.
- La cobertura depende del vocabulario de patrones: una tecnología no incluida no se detectará.
- Los títulos académicos y expresiones de experiencia reconocen vocabulario en inglés; los CV en español necesitan patrones adicionales.
- Los teléfonos se detectan por forma y no se validan contra un plan nacional. El filtro evita formatos de fecha comunes, pero no garantiza que cualquier número restante sea un teléfono.
- Las menciones extraídas no son evidencia de dominio ni se usan para recomendar, clasificar o descartar candidatos.
