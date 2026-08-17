# Definición del proyecto

## Problema

En QA, encontrar antecedentes de un incidente y decidir qué regresión ejecutar puede requerir revisar tickets y casos de prueba dispersos. QA Memory RAG busca reducir esa búsqueda manual usando una base de conocimiento ficticia, trazable y consultable semánticamente.

## Objetivo

Recibir una situación reportada por un tester, recuperar bugs históricos similares y test cases existentes relacionados, y devolver una recomendación fundada en esa evidencia.

La respuesta debe citar los IDs recuperados. Si no hay evidencia suficiente, debe abstenerse en lugar de inventar una recomendación.

## Usuarios

- Tester manual que investiga un incidente o prepara una regresión.
- QA Automation Engineer que necesita antecedentes para elegir cobertura existente.
- Revisor académico que evalúa el flujo RAG, la trazabilidad y la salida JSON.

## Dominio ficticio

La aplicación representa un banco digital con seis módulos:

1. Autenticación y bloqueo de usuarios.
2. Saldos y movimientos.
3. Transferencias.
4. Pago de servicios.
5. Tarjetas y límites.
6. Notificaciones y comprobantes.

## Casos de uso

| ID | Situación reportada | Evidencia esperada | Resultado esperado |
| --- | --- | --- | --- |
| UC-01 | El usuario se bloquea antes del quinto intento. | Bug y casos de autenticación. | Explicar el antecedente y recomendar regresión de intentos y desbloqueo. |
| UC-02 | Una transferencia aprobada no aparece en movimientos. | Bug y casos de saldos e historial. | Relacionar la operación con la consistencia del historial. |
| UC-03 | Una transferencia rechazada descuenta el saldo. | `BUG-TRF-001`, `TC-TRF-004` y `TC-TRF-007`. | Identificar el antecedente crítico y recomendar regresión de rechazo y reversión. |
| UC-04 | Un pago se duplica después de reintentar. | Bug y casos de pagos e idempotencia. | Recomendar validar que exista un único débito. |
| UC-05 | El límite de tarjeta cambia en la interfaz, pero no en backend. | Bug y casos de tarjetas. | Relacionar los controles de interfaz y backend. |
| UC-06 | Una operación exitosa no genera comprobante o notificación. | Bug y casos de notificaciones. | Recomendar validar emisión y visualización del comprobante. |

También se validarán dos comportamientos transversales:

- Una consulta sobre una funcionalidad inexistente debe producir una abstención clara.
- Una consulta de regresión debe recomendar exclusivamente test cases existentes, con sus IDs.

## Alcance

- Un documento de texto plano: `data/faq_document.txt`.
- Al menos 15 bugs ficticios, 20 test cases y una introducción funcional de los módulos.
- Un catálogo técnico mínimo *evidence-only* para los registros ficticios: dominio funcional, servicio o API, endpoint u operación, equipo owner, smoke sugerido, fuente y vigencia.
- Cada dato o relación técnica se expresa como `confirmado`, `parcial` o `desconocido`: sólo lo explícito en la fuente se considera confirmado; no se completan huecos por inferencia.
- Un chunk semántico por bug o test case, con metadata de ID, tipo, módulo y los datos técnicos que estén respaldados.
- Una colección local de Chroma con búsqueda por similitud coseno.
- Dos búsquedas filtradas: `bug` y `test_case`.
- Hasta dos bugs y dos test cases por consulta.
- Una salida JSON con exactamente `user_question`, `system_answer` y `chunks_related`.

La búsqueda MVP continúa separando `bug` y `test_case`. La metadata técnica no agrega filtros en esta primera versión: se preserva dentro de cada elemento de `chunks_related` para que la respuesta sea auditable sin alterar el contrato público.

Un smoke sugerido sólo puede derivarse de evidencia recuperada y se debe etiquetar como sugerencia; no equivale a un test case existente ni a evidencia histórica. Si esa evidencia no alcanza, el sistema debe abstenerse.

## Decisiones técnicas

| Decisión | Elección | Motivo |
| --- | --- | --- |
| Lenguaje | Python 3.12 | Es adecuado para el módulo y mantiene el proyecto accesible. |
| Embeddings | `text-embedding-3-small` | Reduce costo y cubre la necesidad educativa. |
| Generación | Un modelo económico de OpenAI | Resume la evidencia recuperada sin ampliar el alcance. |
| Vector store | Chroma local | Permite persistir y reabrir el índice sin infraestructura externa. |
| Segmentación | Por registro QA completo | Conserva ID, pasos, resultados y trazabilidad. |
| Demo | HTML, CSS y JavaScript nativos | Puede publicarse estáticamente sin backend ni secretos. |

Estas decisiones están implementadas. La suite offline valida el flujo completo sin consumo;
la ruta productiva usa los modelos configurados en `.env`.

## Fuera de alcance

- Datos reales, tickets reales, información personal o bancaria.
- Generación de nuevos test cases o bugs.
- Base SQL, Docker, autenticación, backend público o agentes múltiples.
- Frontend con React, Vite, npm o llamadas directas a OpenAI desde el navegador.
- Conectores a gestores de tickets o fuentes externas.

## Criterios de éxito

- El RAG recupera evidencia relevante en los seis casos de uso.
- Las recomendaciones solo mencionan IDs presentes en la fuente.
- Las relaciones técnicas, owners, endpoints y smokes no se inventan y conservan su fuente, vigencia y estado de evidencia.
- Las consultas sin evidencia reciben abstención, no contenido inventado.
- El proyecto cumple la consigna: 20+ chunks, embeddings, búsqueda vectorial, respuesta JSON y documentación reproducible.
