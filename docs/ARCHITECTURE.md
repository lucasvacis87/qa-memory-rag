# Arquitectura

```text
faq_document.txt -> parser/validación -> chunks completos -> embeddings OpenAI
       -> colección Chroma (coseno) -> búsqueda bug + búsqueda test_case
       -> contexto recuperado -> Responses API -> validación determinística -> JSON
```

## Decisiones

- Un registro QA completo equivale a un chunk. Así se conservan ID, pasos, relaciones y metadata.
- `text-embedding-3-small` genera vectores; Chroma los persiste y calcula similitud coseno.
- Las búsquedas se filtran por `bug` y `test_case` y devuelven hasta dos elementos de cada tipo.
- `gpt-5.4-nano` redacta una respuesta estructurada usando solamente el contexto recuperado.
- Una validación posterior rechaza cualquier ID que no corresponda a un chunk recuperado.
- Los tests inyectan embeddings y generación determinísticos: validan el flujo sin red ni costo.

## Contrato público

La salida tiene exactamente `user_question`, `system_answer` y `chunks_related`. La metadata
técnica vive dentro de cada chunk; no altera los filtros ni agrega claves de primer nivel.

## Fallos seguros

- Sin configuración o índice: error operativo por `stderr` y código de salida distinto de cero.
- Sin evidencia sobre el umbral: abstención sin llamar al generador.
- ID inventado por el modelo: la respuesta se reemplaza por abstención.
- Error de red, cuota o modelo: nunca se cambia silenciosamente de proveedor o modelo.
