# Departamento de CSI
## Computación y Estructuras Discretas III
### 2026-2 — Integrative Task 1

---

# ResumeLens: Formal Language-Based Resume Screening

## Resultados de aprendizaje

- **RAA1** — Aplicar expresiones regulares y teoría de autómatas en la solución de problemas de procesamiento de lenguaje y reconocimiento de patrones.
- **RAA2** — Aplicar conceptos de gramáticas generativas en la implementación de sistemas de procesamiento de lenguajes especializados para dominios o aplicaciones específicas.
- **RAA3** — Simplificar gramáticas mediante formas normales para el procesamiento y análisis eficiente de lenguajes.
- **RAA6** — Comunicar con vocabulario y lenguaje especializado las ideas principales sobre los modelos computacionales estudiados y sus aplicaciones.

---

# 1. Problem Statement

Recruitment processes often require reviewing large numbers of résumés to determine whether candidates satisfy the qualifications expected for a particular professional profile. Although résumés usually contain similar types of information—such as education, professional experience, technical skills, contact information, and projects—the way this information is written and organized may vary considerably.

The same qualification may appear using different names, abbreviations, or spelling conventions. For example, JavaScript, Javascript, and JS may refer to the same programming language; similarly, Scikit-learn, sklearn, and scikit learn refer to the same machine-learning library. In addition, different professional profiles require different combinations of qualifications.

In this project, you will develop **ResumeLens**, an application that processes textual résumés and determines whether the qualifications identified in a candidate's résumé satisfy patterns defined for a professional profile.

ResumeLens will use concepts from formal language theory to address different stages of the problem:

- **Regular expressions** to extract relevant information from résumé text.
- **Finite-state transducers** to normalize different textual representations of equivalent qualifications.
- **Finite automata** to recognize qualification patterns associated with a professional profile.
- **Context-free grammars** to define and validate a structured candidate-profile language.

> **Important:** The purpose of ResumeLens is not to rank candidates or make hiring decisions. The application evaluates whether the qualifications explicitly identified in a résumé satisfy formally defined qualification patterns.

The system must support **four professional profiles** related to software engineering and AI/data-oriented professions.

Two profiles are predefined for all teams:

1. **Full Stack Developer**
2. **Machine Learning Engineer**

---

## Nivel de uso de IAG

### 3. Colaboración con IAG

Los estudiantes pueden apoyarse en la IAG para completar tareas o desarrollar entregables asociados a la actividad, aprovechando las capacidades de estas herramientas para mejorar los productos.

Asimismo, se espera que los estudiantes lleven un registro de sus interacciones con la IAG y estén en la capacidad de modificar los resultados generados, demostrando comprensión y dominio conceptual.

Este registro debe contener tanto el contenido de autoría propia proporcionado a la IAG como los prompts empleados.

---

# 2. Professional Profiles

Each team will additionally define **two other professional profiles**:

- One related to **software engineering**.
- One related to **AI/data**.

Detailed requirements for these profiles will be provided separately.

> The four profiles must be processed through the **same general software solution** rather than through independent implementations.

---

## 2.1 Reference Profile 1 — Full Stack Developer

A Full Stack Developer works with both client-side and server-side components of software applications. This role commonly involves the development of user interfaces, backend services, APIs, database access, and integration among different software components.

For the purposes of this project, a Full Stack Developer profile may include qualifications such as:

- JavaScript or TypeScript
- React, Angular, or Vue
- Node.js, Django, Spring Boot, or a similar backend technology
- SQL or NoSQL databases
- REST APIs
- Git

### Example résumé fragment

```text
Wednesday Addams
3 years of experience developing web applications.
Technical Skills:
JS, React.js, NodeJS, Postgres, Git.
```

ResumeLens must process this information through the different stages of the pipeline before determining whether the candidate satisfies an accepted Full Stack Developer qualification pattern.

---

## 2.2 Reference Profile 2 — Machine Learning Engineer

A Machine Learning Engineer combines software development, data processing, and machine-learning techniques to build computational systems that use predictive or learning-based models.

For the purposes of this project, a Machine Learning Engineer profile may include qualifications such as:

- Python
- Pandas or NumPy
- Scikit-learn
- TensorFlow, or PyTorch
- Machine-learning model development
- SQL
- Git

### Example résumé fragment

```text
Mary Jane Watson
2 years of experience developing predictive models and data-processing pipelines.
Technical Skills:
Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git.
```

As with the Full Stack Developer case, ResumeLens must process the résumé through the complete pipeline before evaluating the qualification pattern.

---

# 3. Main Goal

Develop **ResumeLens**, a résumé-screening system that applies formal language models to:

1. Extract relevant textual information.
2. Normalize equivalent representations.
3. Recognize qualification patterns associated with professional profiles.
4. Validate structured candidate information.

The application must support:

- Full Stack Developer.
- Machine Learning Engineer.
- Two additional professional profiles defined by each team in the areas of:
  - Software engineering.
  - AI/data.

---

# 4. Project Goals

## 4.1 Resume Information Extraction — Regular Expressions

### Objective

Extract relevant textual information from résumés using regular expressions.

Résumés contain information written in different formats. At this stage, the system identifies information that may represent qualifications or candidate data.

It **does not**:

- Determine whether two expressions are equivalent.
- Decide whether the candidate satisfies a job profile.

The first component of ResumeLens must detect elements that may later be used to analyze a candidate, such as:

- Contact information.
- Programming languages.
- Frameworks and libraries.
- Databases.
- Academic qualifications.
- Professional experience.
- Tools and technologies.
- Other qualifications relevant to the supported job profiles.

### Activities for this stage

For each relevant type of information, you must:

- Define the corresponding regular expression.
- Explain the language or textual pattern recognized by the expression.
- Implement the expression using Python's `re` module.
- Keep the extracted information in a file or a data structure.

### Example

Consider the following text in a résumé:

```text
Wednesday Addams
3 years of experience developing web applications.
Technical Skills:
JS, React.js, NodeJS, Postgres, Git.
```

The **Stage 1: extraction** may produce the following strings:

```text
JS
React.js
NodeJS
Postgres
Git
```

**For the next step:** These strings are the input for **Stage 2: Normalization**.

---

# 5. Qualification Normalization — Finite-State Transducers

## Objective

Transform different textual representations of equivalent qualifications into a common canonical representation.

This stage addresses variations in:

- Abbreviations.
- Naming conventions.
- Equivalent textual representations.

**Finite-state transducers** will be used to model these transformations.

---

## 5.1 Formal Definition

For each transducer, you must provide the formal definition using the complete 7-tuple:

```text
M = (Q, Σ, Γ, δ, ω, q0, F)
```

Clearly define:

- **Q** — The set of states.
- **Σ** — The input alphabet.
- **Γ** — The output alphabet.
- **δ** — The transition relation.
- **ω** — The output relation.
- **q0** — The initial state.
- **F** — The set of accepting states.

You must also:

- Provide a graphical representation of the transducers.
- Implement the required transformations using `pyformlang`.

---

## 5.2 Processing

Finite-state transducers must be used to model transformations such as:

| Input | Canonical representation |
|---|---|
| `JS` | `JAVASCRIPT` |
| `Javascript` | `JAVASCRIPT` |
| `React.js` | `REACT` |
| `ReactJS` | `REACT` |
| `NodeJS` | `NODE_JS` |
| `Node.js` | `NODE_JS` |
| `Postgres` | `POSTGRESQL` |
| `PostgreSQL` | `POSTGRESQL` |
| `pandas` | `PANDAS` |
| `sklearn` | `SCIKIT_LEARN` |
| `scikit learn` | `SCIKIT_LEARN` |
| `Scikit-learn` | `SCIKIT_LEARN` |
| `Tensor Flow` | `TENSORFLOW` |
| `TensorFlow` | `TENSORFLOW` |
| `Py Torch` | `PYTORCH` |
| `PyTorch` | `PYTORCH` |

> 🛑 **Note:** These transformations are examples for illustration purposes. You must propose your own transformations.

---

## 5.3 Sorting the Output of the Transformation

The normalized qualifications are prepared as input for the qualification-pattern recognition stage.

Before sending them to the classification automata, the application **may organize** the qualifications in a canonical order defined by the selected professional profile.

This prevents the result from depending on the order in which the candidate wrote the information in the résumé.

### Example order for Full Stack Developer

```text
Full Stack Developer
    ↓
Frontend
    ↓
Backend
    ↓
Database
    ↓
Version control
```

Thus, a résumé containing:

```text
Git, NodeJS, JS, Postgres, React.js
```

produces the normalized and sorted sequence:

```text
JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
```

---

# 6. Qualification Pattern Recognition — Finite Automata

In this stage ResumeLens classify a résumé between the four selected profiles. Then you must determine four profile patterns and use automata to define whether an accepted qualification pattern is satisfied or not.

## Objective

Recognize whether the normalized qualifications satisfy an accepted profile pattern for a professional profile.

At this stage ResumeLens uses **Finite State Automata** to classify the résumé according to the four profiles:

1. Full Stack Developer.
2. Machine Learning Engineer.
3. The first additional profile selected by the students.
4. The second additional profile selected by the students.

For this purpose, students may use:

- Deterministic finite automata.
- Nondeterministic finite automata.
- Nondeterministic finite automata with ε/λ-transitions.

---

## 6.1 Formal Definition

For each automaton, you must provide the formal definition using the complete 5-tuple:

```text
M = (Q, Σ, δ, q0, F)
```

Clearly define:

- **Q** — The set of states.
- **Σ** — The alphabet.
- **δ** — The transition function/relation.
- **q0** — The initial state.
- **F** — The set of accepting states.

You must also:

- Explain the type of automaton (**DFA, NFA, or ε-NFA**) and support your answer considering the previous definition.
- Provide its transition diagram.
- Explain the profile pattern represented by the automaton.
- Implement the automaton using `pyformlang`.

---

## 6.2 Example

For the sequence from the previous stage:

```text
PYTHON, PANDAS, TENSORFLOW, POSTGRESQL, GIT
```

**Profile pattern:**

```text
MACHINE_LEARNING_ENGINEER
```

**Output:**

```text
ACCEPTED
```

---

# 7. Candidate Profile Language — Context-Free Grammars using textX

After the information extraction, normalization and classification, ResumeLens produces a résumé specification and visualization using **Domain Specific Languages** and the **TextX** library.

## Objective

Define a domain-specific language for representing the structured information produced by ResumeLens.

The purpose of this component is different from:

- Extraction.
- Normalization.
- Qualification recognition.

The grammar defines how the resulting candidate information must be structurally represented.

---

## 7.1 Input

The input in this stage is the structured information obtained during the previous stages, such as:

- Candidate information.
- Normalized qualifications.
- Result of the profile classification.

---

## 7.2 Processing

You must define a **DSL for the candidate profile specification** using a context-free grammar and implement it using `textX`.

The language should allow information such as:

- Personal information.
- Contact information.
- Experience.
- Skills.
- The result of the profile classification for each accepted profile.

The language should support structured and repeated elements where appropriate, such as:

- Multiple professional experiences.
- Education records.
- Skills.

---

## 7.3 Activities for this Stage

For your DSL definition you must:

- Define the grammar using **EBNF**, including the identification of terminals and non-terminals.
- Explain the structural characteristics of the language.
- Implement the grammar using `textX`.
- Validate generated candidate profiles.
- Reject representations that violate the lexical or syntactic rules.
- Generate the visualization output.

---

## 7.4 Visualization Output

Once a candidate profile has been successfully validated, the application must use its structured information to generate a short **HTML or Markdown visualization** of the candidate.

For example, a valid candidate profile might produce the following HTML code:

> **[Link]** — download the code and open it using a browser.

---

# 8. Literature Review

Before implementing your program, you should conduct a review of the literature associated with the problem at hand.

This is to:

- Guide the project.
- Avoid redundancies.
- Make informed decisions.
- Develop a solid theoretical foundation.
- Obtain results of high impact and relevance.

---

# 9. Deliverables

## 9.1 Research Poster

1. **Research poster:** [Guide]

---

## 9.2 Design

The design documentation must include:

- Design of modules:
  - Functions.
  - Inputs.
  - Outputs.
- Formalization.
- Design of test cases, including scenarios.

---

## 9.3 Python Implementation

The implementation must contain:

- Complete and correct implementation of the model.
- UI.
- Tests.

---

# 10. Project Presentation

Prepare a **10-minute technical presentation in English** summarizing your project.

The presentation must clearly explain:

- The problem addressed.
- The formal models applied.
- The system architecture.
- The main results obtained.

Use your poster to prepare the presentation.

---

## 10.1 Presentation Requirements

The presentation must be **analytical and technical** in nature.

It should:

- Clearly define the security problem and its relevance in the context of code repositories.
- Explain the methodology, explicitly connecting each system component to its corresponding formal model:
  - Regular expressions.
  - Finite automata.
  - Finite state transducers.
  - Context-free grammars.
- Describe the design decisions made, e.g.:
  - Abstraction level.
  - Alphabet definition.
  - Grammar structure.
  - Classification criteria.
- Present and interpret results, including examples of:
  - Detection.
  - Classification.
  - Transformation.
  - Validation.
- Discuss limitations and possible improvements.

> **Important:** This is not a product demonstration or marketing presentation.

The focus must be on:

- Modeling choices.
- Theoretical justification.
- Implementation strategy.
- The rationale of your decisions as engineers.

Students are expected to demonstrate conceptual understanding of the formal language models they implemented and their practical implications.

---

# 11. Teams

This project can be done in groups of **minimum 2 and maximum 3 people**.

The team must be made up solely and exclusively of people from the **same group (class/section)**.

---

## 11.1 GitHub Repository

You should create your own GitHub repository and then put the link in the file where you register your team.

Please, fill the form to register your team and keep the prefix **En**, where `n` is a number, in the name of your team.

You also need to fill:

- **Course Code**
  - `09772` if you saw this assignment on Intu.
  - `09834` if you saw this on Saman.
- **Group number**
  - `1` for professor Angela.
  - `3` for professor Andres.
  - `5` for Juan Marcos.

---

## 11.2 Commit Requirements

Your repository must have at least **10 commits** with a difference of at least **2 hours between each of them**.

These commits must be meaningful in terms of value.

For example, they cannot be simply:

- Deleting a variable.
- Changing a method name.

---

## 11.3 Project Documentation

In the repository or project, there should be a directory called:

```text
docs/
```

Each of the design documents should be placed there.

Documents in your repository should be written using **Markdown**.

Include any necessary clarifications for manipulating or understanding your project in the `README.md` file as extra documentation.

For example:

- IDE used.
- Members’ names.

The contribution of each member will be evaluated based on their input, and the only way to verify this will be through the commits.

> **Note:** The poster, as well as the presentation or demonstration showcasing the functionality and features of the system, must be in **English**.

---

# 12. Deadline

## **11th of October, 2026**

---

# 13. Project Pipeline

The complete ResumeLens process can be represented as the following sequence:

```text
                    ┌─────────────────────┐
                    │   Résumé Text      │
                    └──────────┬──────────┘
                               │
                               ▼
              ┌─────────────────────────────┐
              │  1. Regular Expressions     │
              │       Extraction             │
              └──────────────┬──────────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │  2. Finite-State            │
              │     Transducers              │
              │     Normalization             │
              └──────────────┬──────────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │  3. Finite Automata         │
              │     Profile Recognition      │
              └──────────────┬──────────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │  4. Context-Free Grammar    │
              │     + textX                  │
              │     Structured Profile       │
              └──────────────┬──────────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │ HTML / Markdown             │
              │ Visualization                │
              └─────────────────────────────┘
```

---

# 14. Quick Requirements Checklist

## Formal models

- [ ] Regular expressions defined and implemented with Python `re`.
- [ ] Finite-state transducers formally defined using a complete 7-tuple.
- [ ] Finite-state transducers represented graphically.
- [ ] Transducers implemented using `pyformlang`.
- [ ] Four professional profiles defined.
- [ ] Finite automata formally defined using a complete 5-tuple.
- [ ] Automaton type explained: DFA, NFA, or ε-NFA.
- [ ] Transition diagrams provided.
- [ ] Automata implemented using `pyformlang`.
- [ ] Context-free grammar defined using EBNF.
- [ ] Terminals and non-terminals identified.
- [ ] Grammar implemented using `textX`.
- [ ] Invalid lexical/syntactic representations rejected.
- [ ] HTML or Markdown visualization generated.

## Software project

- [ ] Complete Python implementation.
- [ ] UI.
- [ ] Tests.
- [ ] Design documentation.
- [ ] `docs/` directory.
- [ ] `README.md`.
- [ ] Own GitHub repository.
- [ ] Minimum 10 meaningful commits.
- [ ] At least 2 hours between commits.

## Presentation and documentation

- [ ] Research poster.
- [ ] 10-minute technical presentation.
- [ ] Poster in English.
- [ ] Presentation in English.
- [ ] Demonstration in English.
- [ ] Literature review.
- [ ] Design of modules and inputs/outputs.
- [ ] Formalization.
- [ ] Test cases and scenarios.

## Team

- [ ] 2–3 students.
- [ ] All students from the same class/section.
- [ ] Team registered.
- [ ] Course code registered.
- [ ] Group number registered.

## Deadline

- [ ] **October 11, 2026**

