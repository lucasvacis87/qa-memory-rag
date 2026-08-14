# Guardrails

## Datos

- La base de conocimiento debe ser completamente ficticia.
- Están prohibidos datos bancarios reales, datos personales, credenciales, tickets internos o incidentes reales.
- Los ejemplos de consultas y respuestas deben conservar ese mismo carácter ficticio.

## Evidencia y respuestas

- El modelo puede resumir y relacionar chunks recuperados, pero no crear evidencia.
- No puede inventar IDs, bugs, test cases, pasos, resultados esperados o relaciones.
- Debe mencionar los IDs que respaldan sus recomendaciones.
- Si la recuperación no entrega evidencia suficiente, debe abstenerse de forma explícita.

## Secretos y costos

- La API key se guarda únicamente en `.env`, nunca en código, documentación, salidas, commits o demo web.
- `.env` e índices locales deben ignorarse en Git cuando existan.
- Toda carga de saldo, cambio de modelo pago o activación de recarga automática requiere aprobación explícita.
- Antes de cargar saldo se revisará nuevamente el precio y la disponibilidad oficial.

## Límites técnicos

- Un único documento fuente y una única colección Chroma.
- Dos filtros simples: `bug` y `test_case`.
- Sin SQL, Docker, backend público, autenticación, agentes múltiples ni abstracciones prematuras.
- La demo estática no tendrá API key, backend ni llamadas a OpenAI.

## Calidad mínima

- El contrato público tendrá exactamente tres claves: `user_question`, `system_answer` y `chunks_related`.
- Los errores operativos deben ir a `stderr`, sin exponer secretos.
- Los cambios de fuente, recuperación, modelo o formato obligan a actualizar la documentación y las pruebas relevantes.
