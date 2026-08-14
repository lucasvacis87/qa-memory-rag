# QA Memory RAG

## Estado

Proyecto en preparación. La documentación de producto y la estructura mínima del repositorio están listas. Todavía no hay corpus QA, credenciales, embeddings, índice Chroma ni pipeline RAG implementado.

## Idea

QA Memory RAG será una memoria histórica de QA para una aplicación ficticia de banca digital. Un tester describe una situación y el sistema recupera bugs históricos y test cases ya existentes para explicar los antecedentes y recomendar regresión respaldada por evidencia.

El sistema no crea test cases, no inventa IDs y se abstiene cuando no encuentra evidencia suficiente.

Ejemplo de consulta:

> “La transferencia fue rechazada, pero se descontó el saldo. ¿Qué antecedentes existen y qué regresión conviene ejecutar?”

El resultado esperado es una respuesta con bugs similares, test cases existentes recomendados y sus identificadores.

## Flujo previsto

```text
Situación QA
  -> embedding de la consulta
  -> bugs similares + test cases relacionados
  -> contexto con evidencia recuperada
  -> recomendación fundamentada o abstención
```

## Documentación

- [Definición del proyecto](docs/PROJECT_BRIEF.md)
- [Roadmap](docs/ROADMAP.md)
- [Guardrails](docs/GUARDRAILS.md)
- [Guía de trabajo para agentes](AGENTS.md)

La consigna original se conserva en `Consignas Proyecto 2 RAG.docx` y funciona como referencia de evaluación.

## Preparación del entorno

Requisitos locales:

- Git.
- Python 3.12.
- PowerShell.

Desde la raíz del repositorio:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Para confirmar que el entorno usa la versión correcta:

```powershell
python --version
python -c "import src; print('QA Memory RAG listo')"
```

La API key no se configura en esta historia. `.env.example` es solamente una plantilla segura; el archivo `.env` real se creará localmente durante la HU-03 y Git lo ignorará.

## Estructura inicial

```text
data/       futura base de conocimiento QA ficticia
docs/       definición, roadmap y reglas del proyecto
outputs/    resultados locales y ejemplos generados
scripts/    utilidades ejecutables para inspección y validación
src/        código fuente del proyecto
tests/      pruebas automáticas
```

El código y la documentación se versionan. `.venv`, `.env`, cachés, índices locales de Chroma y resultados regenerables permanecen fuera de Git.

## Límites de la primera versión

- Toda la información será ficticia: no se usarán datos bancarios, personales ni incidentes reales.
- Habrá un único documento fuente, una colección vectorial local y filtros por tipo de registro.
- No habrá backend público, autenticación, Docker, base SQL, agentes múltiples ni frontend con frameworks.
- La futura demo web mostrará resultados ficticios precalculados y no contendrá una API key.

## Próximo hito

HU-03: configurar OpenAI de forma segura y comprobar la cuenta sin exponer credenciales ni avanzar todavía con embeddings, indexación o búsqueda.
