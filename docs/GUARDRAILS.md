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
- La metadata técnica ficticia —dominio funcional, servicio o API, endpoint u operación, equipo owner, smoke sugerido, fuente y vigencia— sólo se conserva si está respaldada por la fuente.
- Cada dato o relación técnica debe indicar `confirmado`, `parcial` o `desconocido`. `Parcial` no habilita completar datos, y `desconocido` nunca se reemplaza por una inferencia.
- Un smoke sugerido debe estar etiquetado como tal; no es un test case ni evidencia histórica salvo que la fuente lo registre explícitamente.

## Secretos y costos

- La API key se guarda únicamente en `.env`, nunca en código, documentación, salidas, commits o demo web.
- `.env` e índices locales deben ignorarse en Git cuando existan.
- Antes de crear un cliente o iniciar una llamada de red, la configuración local debe validar API key y modelos; los errores van a `stderr` y no incluyen valores de variables de entorno.
- Toda carga de saldo, cambio de modelo pago o activación de recarga automática requiere aprobación explícita.
- Antes de cargar saldo se revisará nuevamente el precio y la disponibilidad oficial.

## Límites técnicos

- Un único documento fuente y una única colección Chroma.
- Dos filtros simples: `bug` y `test_case`.
- La metadata técnica se preserva dentro de los elementos de `chunks_related`; no agrega filtros técnicos al MVP ni modifica el contrato público.
- Sin SQL, Docker, backend público, autenticación, agentes múltiples ni abstracciones prematuras.
- La demo estática no tendrá API key, backend ni llamadas a OpenAI.
- Un conector externo queda fuera de estos cinco sprints; cuando se evalúe, deberá ser *read-only* y normalizar fuente, vigencia y estado de evidencia antes de indexar.

## Calidad mínima

- El contrato público tendrá exactamente tres claves: `user_question`, `system_answer` y `chunks_related`.
- Los errores operativos deben ir a `stderr`, sin exponer secretos.
- Los cambios de fuente, recuperación, modelo o formato obligan a actualizar la documentación y las pruebas relevantes.
