# Roadmap

No hay fechas comprometidas. Se trabaja una sola historia por vez y cada etapa termina con una validación antes de avanzar.

## Sprint 0 — Fundamentos y entorno

- HU-01 (completada): entender el problema de QA, diferenciar recuperación de generación y validar el flujo RAG aplicado a QA.
- HU-02: preparar Git, Python, entorno virtual y estructura mínima.
- HU-03: configurar de manera segura la cuenta y la API de OpenAI.

**Resultado:** entorno reproducible y un flujo RAG entendido antes de consumir APIs.

## Sprint 1 — Base de conocimiento QA

- HU-04: diseñar al menos 15 bugs históricos ficticios.
- HU-05: diseñar al menos 20 test cases existentes y trazables.
- HU-06: construir y validar `data/faq_document.txt`.

**Resultado:** una fuente ficticia, UTF-8, con IDs únicos, módulos y relaciones bug–test case claras.

## Sprint 2 — Chunking, embeddings e índice local

- HU-07: cargar y limpiar la fuente.
- HU-08: crear chunks completos por registro QA.
- HU-09: probar embeddings con situaciones QA.
- HU-10: crear y persistir el índice local de Chroma.

**Resultado:** documento procesado, 20 o más chunks con metadata y un índice que se puede reabrir.

## Sprint 3 — Recuperación QA

- HU-11: buscar únicamente bugs similares.
- HU-12: buscar únicamente test cases relacionados.
- HU-13: combinar ambas búsquedas en una vista clara.

**Resultado:** resultados separados por tipo, filtrados por metadata y limitados a cuatro chunks totales.

## Sprint 4 — Respuestas, calidad y evaluación

- HU-14: generar recomendación fundamentada o abstención.
- HU-15: aplicar el contrato JSON público.
- HU-16: evaluar relevancia de consultas de los seis módulos.
- HU-17: agregar pruebas y manejo de errores.
- HU-18: implementar el evaluador bonus si el flujo principal ya es estable.

**Resultado:** pipeline completo, comprobable y con al menos 80% de evidencia relevante en ejemplos.

## Sprint 5 — Demo y entrega

- HU-19: crear demo visual estática con resultados ficticios precalculados.
- HU-20: publicar GitHub Pages desde `main/docs`.
- HU-21: documentar, probar un clon limpio y preparar la entrega.

**Resultado:** repositorio autocontenido, sin secretos y navegable para evaluación.

## Puertas de avance

| Antes de avanzar a | Debe verificarse |
| --- | --- |
| Sprint 2 | La base contiene bugs, test cases y trazabilidad completos. |
| Sprint 3 | Los chunks conservan ID, tipo, módulo y contenido útil. |
| Sprint 4 | El índice local se construye y se vuelve a abrir correctamente. |
| Sprint 5 | El JSON cumple el contrato y las consultas sin evidencia se abstienen. |
| Entrega | Tests, documentación, secretos y clon limpio revisados. |
