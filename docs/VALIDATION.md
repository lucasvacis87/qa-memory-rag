# Evidencia de validación

## Suite automatizada

- Parser, IDs duplicados, relaciones y volumen de la fuente.
- Chunks completos de 50 a 500 tokens aproximados.
- Construcción, persistencia y reapertura de Chroma.
- Filtros separados y límite de resultados.
- Contrato JSON exacto, abstención e IDs inventados.
- Configuración sin secretos y costos separados.

Ejecutar: `python -m pytest -q`.

## Validación real

La prueba real requiere `.env`, saldo y acceso a ambos modelos. Se ejecuta primero
`python -m src.cli build-index` y luego consultas representativas. Los resultados públicos se
sanitizan y la demo conserva muestras offline reproducibles para no publicar credenciales ni
depender de servicios externos.

Validación real realizada el 16 de agosto de 2026:

- 37 chunks indexados con `text-embedding-3-small`.
- 7.119 tokens de embeddings y costo estimado de USD 0,00014238.
- UC-03 recuperó `BUG-TRF-001`, `TC-TRF-004` y `TC-TRF-007`; la respuesta pasó el control de IDs.
- La consulta fuera de dominio sobre cultivo devolvió abstención y cero chunks.
- CI en `main` y despliegue de GitHub Pages finalizaron correctamente.
- Demo pública: <https://lucasvacis87.github.io/qa-memory-rag/>.

### Migración LangChain — 17 de agosto de 2026

- Entorno recreado con Python 3.13 y dependencias verificadas mediante `pip check`.
- Suite offline completa: 29 tests aprobados sin llamadas de red.
- Versiones verificadas: `langchain==1.3.14`, `langchain-openai==1.4.1`,
  `langchain-chroma==1.1.0`, `chromadb==1.5.9` y `openai==2.54.0`.
- Indexación real mediante `OpenAIEmbeddings` y `langchain-chroma`: 37 chunks con
  `text-embedding-3-small`, 7.119 tokens y costo estimado de USD 0,00014238.
- Consulta real mediante `ChatPromptTemplate`, `ChatOpenAI`, Responses API y Structured
  Outputs: recuperó `BUG-TRF-001`, `TC-TRF-004` y `TC-TRF-007` como evidencia principal.
- Evaluación de la consulta: 10/10, IDs válidos, evidencia esperada presente y contrato JSON
  limitado a `user_question`, `system_answer` y `chunks_related`.
