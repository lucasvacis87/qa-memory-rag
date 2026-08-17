# Evidencia de validación

## Suite automatizada

- Parser, IDs duplicados, relaciones y volumen de la fuente.
- Chunks completos de 50 a 500 palabras aproximadas.
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
