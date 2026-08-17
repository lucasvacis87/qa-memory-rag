# QA Memory RAG

RAG educativo aplicado a memoria histórica de QA para un banco digital ficticio. Recibe una
situación, recupera bugs y test cases existentes y devuelve una recomendación trazable. Si la
evidencia no alcanza, se abstiene.

## Qué entrega

- Fuente UTF-8 de 3.600+ palabras: 15 bugs, 22 test cases y seis módulos.
- Un chunk completo por registro con metadata técnica *evidence-only*.
- Embeddings `text-embedding-3-small` y colección Chroma local con similitud coseno.
- Hasta dos bugs y dos test cases por consulta.
- Generación con Responses API y `gpt-5.4-nano`.
- JSON con exactamente `user_question`, `system_answer` y `chunks_related`.
- 34+ tests offline, evaluador determinístico, ejemplos y [demo estática](https://lucasvacis87.github.io/qa-memory-rag/).

## Requisitos e instalación

- Python 3.12 o 3.13.
- Una API key de OpenAI con saldo y acceso a los modelos configurados.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Editá `.env` localmente y reemplazá solamente `OPENAI_API_KEY`. El archivo está ignorado por
Git. No compartas la clave por chat, capturas, logs ni commits.

## Uso

```powershell
python -m src.cli validate-source
python -m src.cli build-index
python -m src.cli query "Una transferencia rechazada descontó el saldo" --evaluate
python -m pytest -q
python scripts/generate_samples.py
python -m http.server 8000 --directory docs
```

La indexación informa cantidad de chunks, tokens estimados y costo estimado. El costo de
embeddings se calcula aparte de la generación. Los precios son configurables en
`src/pricing.py` y deben revisarse antes de una entrega futura.

## Estructura

```text
data/faq_document.txt       fuente ficticia
src/source.py               parser y validación
src/index.py                Chroma y recuperación
src/providers.py            OpenAI y dobles offline
src/rag.py                  pipeline y guardrail de IDs
src/evaluation.py           evaluador determinístico
src/cli.py                  consola
outputs/sample_queries.json ejemplos versionados
docs/                       arquitectura y demo pública
tests/                      suite sin consumo de API
```

## Seguridad y límites

Todo el contenido de negocio es ficticio. El sistema no genera bugs ni casos nuevos, no usa
datos bancarios reales y no publica un backend. La demo contiene resultados precalculados y
no realiza llamadas a OpenAI. Un smoke sólo puede aparecer como sugerencia derivada de la
evidencia; nunca se presenta como test case histórico.

La especificación completa está en [PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md), los límites en
[GUARDRAILS.md](docs/GUARDRAILS.md), la arquitectura en [ARCHITECTURE.md](docs/ARCHITECTURE.md)
y la consigna original en [Consignas_proyecto.md](Consignas_proyecto.md).

## Troubleshooting

- `El índice no existe`: ejecutá `build-index` con la misma configuración.
- `401`: revisá sólo tu `.env` local; nunca imprimas la key.
- `429` o cuota: verificá saldo/límites y no cambies de modelo automáticamente.
- Modelo sin acceso: conservá el error y elegí otro modelo sólo mediante una decisión explícita.
- Entorno virtual roto: recrealo con el Python instalado; no reutilices rutas de una instalación eliminada.
