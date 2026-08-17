# Arquitectura

```text
faq_document.txt -> parser/validación -> chunks completos -> LangChain OpenAIEmbeddings
       -> langchain-chroma -> colección ChromaDB (coseno)
       -> búsqueda bug + búsqueda test_case -> contexto recuperado
       -> ChatPromptTemplate -> ChatOpenAI/Responses API/Structured Outputs
       -> validación determinística -> JSON
```

## Decisiones

- Un registro QA completo equivale a un chunk. Así se conservan ID, pasos, relaciones y metadata.
- `OpenAIEmbeddings` de LangChain usa `text-embedding-3-small`; ChromaDB persiste los vectores
  mediante `langchain-chroma` y calcula distancia coseno.
- Las búsquedas se filtran por `bug` y `test_case` y devuelven hasta dos elementos de cada tipo.
- `ChatPromptTemplate` compone instrucciones, pregunta y evidencia recuperada.
- `ChatOpenAI` usa explícitamente Responses API y `gpt-5.4-nano`; Structured Outputs exige el
  campo interno `system_answer` antes de construir el contrato público.
- Una validación posterior rechaza cualquier ID que no corresponda a un chunk recuperado.
- Los tests inyectan `Embeddings` y `Runnable` determinísticos: validan el flujo sin red ni costo.

LangChain orquesta integraciones, pero no decide si una respuesta está respaldada. El umbral,
la separación por tipo, la validación de IDs, la abstención y el JSON final siguen siendo reglas
determinísticas del proyecto.

## Contrato público

La salida tiene exactamente `user_question`, `system_answer` y `chunks_related`. La metadata
técnica vive dentro de cada chunk; no altera los filtros ni agrega claves de primer nivel.

## Fallos seguros

- Sin configuración o índice: error operativo por `stderr` y código de salida distinto de cero.
- Sin evidencia sobre el umbral: abstención sin llamar al generador.
- ID inventado por el modelo: la respuesta se reemplaza por abstención.
- Error de red, cuota o modelo: nunca se cambia silenciosamente de proveedor o modelo.
