# Roadmap

No hay fechas comprometidas. Se trabaja una sola historia por vez y cada etapa termina con una validación antes de avanzar.

## Sprint 0 — Fundamentos y entorno

- HU-01 (completada): entender el problema de QA, diferenciar recuperación de generación y validar el flujo RAG aplicado a QA.
- HU-02 (completada): preparar Git, Python, entorno virtual y estructura mínima.
- HU-03 (completada): configurar de manera segura la cuenta y la API de OpenAI.

**Resultado:** entorno reproducible y un flujo RAG entendido antes de consumir APIs.

## Sprint 1 — Base de conocimiento QA

- HU-04 (completada): definir el catálogo técnico mínimo *evidence-only*.
- HU-05 (completada): diseñar al menos 15 bugs históricos ficticios.
- HU-06 (completada): diseñar al menos 20 test cases existentes y trazables.
- HU-07 (completada): construir y validar `data/faq_document.txt`.

**Resultado:** una fuente ficticia, UTF-8, con IDs únicos, módulos, metadata técnica respaldada y relaciones bug–test case claras.

### HU-04 — Catálogo técnico mínimo *evidence-only*

Define, antes de redactar los registros QA, los campos técnicos ficticios que pueden acompañar cada evidencia: dominio funcional, servicio o API, endpoint u operación, equipo owner, smoke sugerido, fuente y vigencia. Cada campo o relación debe quedar marcado como `confirmado`, `parcial` o `desconocido`.

No se completa información por inferencia: `confirmado` exige respaldo explícito en la fuente; `parcial` conserva sólo lo disponible; `desconocido` expresa la ausencia de evidencia. Un smoke sugerido debe estar respaldado por la evidencia y nunca se presenta como cobertura histórica existente.

## Sprint 2 — Chunking, embeddings e índice local

- HU-08 (completada): cargar y limpiar la fuente.
- HU-09 (completada): crear chunks completos por registro QA y preservar su metadata técnica.
- HU-10 (completada): probar embeddings con situaciones QA.
- HU-11 (completada): crear y persistir el índice local de Chroma.

**Resultado:** documento procesado, 20 o más chunks con metadata y un índice que se puede reabrir.

## Sprint 3 — Recuperación QA

- HU-12 (completada): buscar únicamente bugs similares.
- HU-13 (completada): buscar únicamente test cases relacionados.
- HU-14 (completada): combinar ambas búsquedas en una vista clara.

**Resultado:** resultados separados por tipo (`bug` y `test_case`) y limitados a cuatro chunks totales; la metadata técnica queda preservada para auditoría, sin filtros técnicos en el MVP.

## Sprint 4 — Respuestas, calidad y evaluación

- HU-15 (completada): generar recomendación fundamentada o abstención, distinguiendo evidencia confirmada, parcial y desconocida.
- HU-16 (completada): aplicar el contrato JSON público.
- HU-17 (completada): evaluar relevancia de consultas de los seis módulos y la integridad de la metadata preservada.
- HU-18 (completada): agregar pruebas y manejo de errores, incluida la no invención de IDs, relaciones y metadata.
- HU-19 (completada): implementar el evaluador bonus si el flujo principal ya es estable.

**Resultado:** pipeline completo, comprobable y con al menos 80% de evidencia relevante en ejemplos.

## Sprint 5 — Demo y entrega

- HU-20 (completada): crear demo visual estática con resultados ficticios precalculados.
- HU-21 (lista para publicar): publicar GitHub Pages desde `main/docs`.
- HU-22 (en validación final): documentar, probar un clon limpio y preparar la entrega.

**Resultado:** repositorio autocontenido, sin secretos y navegable para evaluación.

## Puertas de avance

| Antes de avanzar a | Debe verificarse |
| --- | --- |
| Sprint 2 | La base contiene bugs, test cases, trazabilidad completa y metadata técnica con fuente, vigencia y estado de evidencia. |
| Sprint 3 | Los chunks conservan ID, tipo, módulo y contenido útil. |
| Sprint 4 | El índice local se construye y se vuelve a abrir correctamente. |
| Sprint 5 | El JSON cumple el contrato y las consultas sin evidencia se abstienen. |
| Entrega | Tests, documentación, secretos y clon limpio revisados. |

## Límites de integración

El MVP conserva las búsquedas separadas por `bug` y `test_case`; la metadata técnica se preserva dentro de cada elemento de `chunks_related`, sin agregar filtros técnicos como requisito inicial. El contrato público no cambia.

Un conector externo no integra estos cinco sprints. Será una etapa futura, *read-only*, que deberá normalizar su fuente y conservar fuente, vigencia y estados de evidencia antes de indexar; no se harán consultas remotas en vivo por cada pregunta.
