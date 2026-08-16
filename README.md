# QA Memory RAG

QA Memory RAG es una memoria histórica de QA para una aplicación ficticia de banca digital. Recibe una situación reportada por un tester, recupera bugs históricos y test cases existentes relacionados, y recomienda una regresión respaldada por esa evidencia. El objetivo es reducir la búsqueda manual entre antecedentes dispersos sin que el sistema invente bugs, IDs, pasos, resultados esperados ni cobertura nueva.

## Qué resuelve

Un tester o QA Automation Engineer puede describir un incidente —por ejemplo, “la transferencia fue rechazada, pero se descontó el saldo”— y obtener:

- Bugs históricos similares.
- Test cases existentes para ejecutar como regresión.
- Una recomendación fundamentada con los IDs recuperados.
- Una abstención explícita cuando no haya evidencia suficiente.

## Alcance funcional

El dominio ficticio cubre seis módulos de banca digital:

1. Autenticación y bloqueo de usuarios.
2. Saldos y movimientos.
3. Transferencias.
4. Pago de servicios.
5. Tarjetas y límites.
6. Notificaciones y comprobantes.

La base de conocimiento contendrá bugs y test cases ficticios, trazables por ID, tipo y módulo. El sistema recuperará hasta dos bugs y dos test cases por consulta.

## Arquitectura

```text
Situación QA
  -> embedding de la consulta
  -> búsqueda separada de bugs y test cases
  -> evidencia recuperada y filtrada
  -> recomendación fundamentada o abstención
  -> JSON auditable
```

Primero se recupera evidencia y recién después se genera la respuesta. Esa separación hace que el conocimiento sea actualizable, trazable y verificable.

## Tecnologías

| Tecnología | Rol | Uso en el proyecto |
| --- | --- | --- |
| Python 3.12 | Lenguaje principal | Ejecuta carga, indexación, consulta y pruebas. |
| OpenAI API | Embeddings y LLM | Genera vectores con `text-embedding-3-small` y redacta la respuesta a partir de la evidencia recuperada. |
| ChromaDB | Vector store local | Persiste los vectores y recupera registros similares por significado. |
| tiktoken | Conteo de tokens | Verifica que los chunks respeten el rango de 50 a 500 tokens. |
| python-dotenv | Configuración | Carga variables locales desde `.env` sin versionar secretos. |
| pytest | Pruebas automatizadas | Valida carga, chunking, recuperación, contrato JSON y errores. |
| Git y GitHub | Control de versiones | Conservan el historial y publican el repositorio de entrega. |

**Embeddings** son números que representan el significado de un texto y permiten comparar consultas con registros existentes. Un **LLM** es el modelo de lenguaje que redacta la respuesta final; en este proyecto sólo puede usar la evidencia recuperada.

## Requisitos

- Git.
- Python 3.12.
- PowerShell en Windows.
- Una API key de OpenAI para ejecutar embeddings y generación.

## Instalación

Desde la raíz del repositorio:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Comprobá el entorno:

```powershell
python --version
python -c "import src; print('QA Memory RAG listo')"
```

## Configuración

Creá tu archivo local de configuración a partir de la plantilla:

```powershell
Copy-Item .env.example .env
```

Completá `.env` con tus valores locales:

```dotenv
OPENAI_API_KEY=your-key-here
EMBEDDING_MODEL=text-embedding-3-small
RESPONSE_MODEL=your-response-model
```

`.env` nunca debe subirse al repositorio, incluirse en capturas, salidas, documentación o demo web. La key se lee desde variables de entorno y no se imprime en logs.

## Uso

La interfaz pública del proyecto es la siguiente:

```powershell
# Construir o actualizar el índice local
python src/build_index.py

# Consultar antecedentes y regresión recomendada
python src/query.py "La transferencia fue rechazada, pero se descontó el saldo"

# Ejecutar las pruebas
python -m pytest
```

`build_index.py` procesa `data/faq_document.txt`, genera chunks, embeddings y el índice local. `query.py` transforma la consulta en embedding, recupera evidencia y devuelve exclusivamente JSON por salida estándar. Los errores operativos se informan por `stderr`.

## Contrato de salida

Cada consulta devuelve exactamente tres claves de primer nivel:

```json
{
  "user_question": "La transferencia fue rechazada, pero se descontó el saldo",
  "system_answer": "Se encontró evidencia relacionada. Ejecutar los test cases indicados para validar rechazo y reversión.",
  "chunks_related": [
    {
      "id": "BUG-TRF-001",
      "type": "bug",
      "module": "transferencias",
      "content": "...",
      "similarity_score": 0.91
    }
  ]
}
```

`system_answer` debe citar los IDs que respaldan la recomendación. Si la recuperación no entrega evidencia suficiente, debe abstenerse de forma explícita. No se generan bugs ni test cases nuevos.

## Base de conocimiento y recuperación

- Fuente: `data/faq_document.txt` en UTF-8.
- Contenido mínimo: 15 bugs ficticios, 20 test cases existentes y una introducción funcional del dominio.
- Chunking: un registro QA completo por chunk para conservar ID, módulo, pasos, resultado esperado y trazabilidad.
- Tamaño: entre 50 y 500 tokens por chunk.
- Recuperación: similitud coseno en una colección local de Chroma.
- Filtros: búsquedas separadas por `bug` y `test_case`.
- Límite: hasta dos registros de cada tipo por consulta.

## Estructura del proyecto

```text
data/
  faq_document.txt       base de conocimiento ficticia
docs/
  PROJECT_BRIEF.md       definición funcional
  GUARDRAILS.md          reglas de seguridad y evidencia
  ROADMAP.md             secuencia de implementación
outputs/
  sample_queries.json    ejemplos de consultas y respuestas
scripts/                 utilidades de inspección y validación
src/
  build_index.py         pipeline de indexación
  query.py               pipeline de consulta
tests/                   pruebas automatizadas
Consignas_proyecto.md    consigna académica migrada a Markdown
requirements.txt         dependencias fijadas
.env.example             plantilla de configuración
```

Los directorios `.venv`, `.env`, cachés, índices locales de Chroma y salidas regenerables están ignorados por Git. `outputs/sample_queries.json` es la excepción: se versiona como evidencia de funcionamiento.

## Calidad y seguridad

- Toda la información es ficticia: no se usan datos personales, bancarios, tickets ni incidentes reales.
- La respuesta puede resumir y relacionar chunks recuperados, pero no inventar evidencia.
- Las consultas sin respaldo producen abstención.
- La demo web es estática y no contiene API keys, backend ni llamadas a OpenAI.
- No hay SQL, Docker, autenticación, backend público, agentes múltiples ni frontend con frameworks dentro de este alcance.

## Documentación relacionada

- [Definición funcional](docs/PROJECT_BRIEF.md)
- [Guardrails](docs/GUARDRAILS.md)
- [Roadmap de implementación](docs/ROADMAP.md)
- [Consigna académica](Consignas_proyecto.md)
