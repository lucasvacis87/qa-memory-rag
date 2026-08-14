# HU-01 — Problema de QA y arquitectura RAG

## Problema

Un tester que investiga un incidente suele buscar antecedentes en bugs y test cases dispersos. QA Memory RAG reduce esa búsqueda manual: recibe una situación escrita en lenguaje natural, recupera registros QA ficticios similares y devuelve una respuesta trazable.

Ejemplo:

> Una transferencia fue rechazada, pero se descontó el saldo. ¿Qué antecedentes existen y qué regresión conviene ejecutar?

## Recuperar antes de generar

Recuperar significa buscar bugs y test cases que ya existen en la base de conocimiento. Generar significa redactar una respuesta clara usando únicamente esos registros como contexto.

El modelo no crea evidencia: no puede inventar bugs, test cases, IDs, pasos ni resultados esperados. Si no hay evidencia relevante, debe abstenerse.

## Flujo de consulta

```text
Situación QA
  → embedding de la pregunta
  → búsqueda semántica de bugs y test cases
  → contexto con IDs y contenido recuperado
  → LLM
  → explicación y recomendación trazable, o abstención
```

Limitar al modelo al contexto recuperado reduce alucinaciones: la respuesta se apoya en registros concretos que luego pueden localizarse por ID.

## Pipeline de indexación

Se ejecuta al crear o actualizar la base de conocimiento:

```text
documento fuente
  → carga UTF-8 y limpieza
  → un chunk por registro QA completo
  → embeddings
  → índice vectorial local
```

Cada chunk conserva `record_id`, `record_type`, `module` y el contenido del registro.

## Pipeline de consulta

Se ejecuta para cada pregunta del tester:

```text
pregunta
  → embedding con el mismo modelo
  → búsqueda por similitud, separada por tipo
  → hasta 2 bugs y 2 test cases
  → contexto recuperado
  → respuesta JSON
```

El LLM se llama después de recuperar el contexto, no antes.

## Contrato público

La salida tendrá exactamente estas claves:

```json
{
  "user_question": "Al rechazar una transferencia se descontó el saldo.",
  "system_answer": "Respuesta basada en la evidencia recuperada.",
  "chunks_related": []
}
```

`chunks_related` preserva los IDs y metadata para auditar qué evidencia se usó.

## Cierre de aprendizaje

HU-01 completada el 14 de agosto de 2026. Lucas explicó correctamente que, antes de llamar al LLM, se generan el embedding de la pregunta y el contexto recuperado; esto evita que el modelo responda sin basarse en información del bug o los test cases existentes.
