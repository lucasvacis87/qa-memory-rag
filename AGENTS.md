# Guía de colaboración

## Antes de modificar el proyecto

1. Leer `README.md` y `docs/PROJECT_BRIEF.md`.
2. Revisar `docs/GUARDRAILS.md` antes de trabajar con datos, APIs o publicación.
3. Avanzar una historia a la vez, según `docs/ROADMAP.md`.

## Principios de implementación

- Mantener Python simple, modular y legible; cada función debe tener una responsabilidad clara.
- Usar UTF-8 y nombres descriptivos en inglés para código e identificadores; la documentación y los ejemplos pueden estar en español.
- Ejecutar los comandos desde la raíz del repositorio y documentar cualquier comando nuevo en el README cuando exista.
- Incorporar cambios pequeños, con una prueba aislada antes de seguir con el siguiente paso.
- Preservar los IDs de bugs y test cases: son la trazabilidad entre la fuente, el índice y la respuesta.

## Regla funcional central

El RAG solo puede resumir, relacionar y recomendar evidencia recuperada. Nunca puede crear bugs, test cases, pasos, resultados esperados ni IDs que no estén en la base de conocimiento.

Si la evidencia no alcanza, debe responder con una abstención explícita.

## Validación futura

El orden mínimo de validación será:

1. Inspeccionar el documento fuente.
2. Revisar sus chunks y metadata.
3. Construir y reabrir el índice local.
4. Probar búsqueda de bugs y test cases por separado.
5. Probar la consulta RAG completa y su contrato JSON.
6. Ejecutar tests antes de actualizar salidas de ejemplo o demo.

## Actualización de documentación

Actualizar el brief y los guardrails si cambia el alcance, el modelo, la fuente de datos, el formato de salida, la estrategia de recuperación o cualquier integración externa.
