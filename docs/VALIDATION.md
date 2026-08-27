# Validation evidence

## Automated suite

- Parser, duplicate IDs, relationships, and source volume.
- Complete chunks between approximately 50 and 500 tokens.
- Chroma construction, persistence, and reopening.
- Separate filters and result limits.
- Exact JSON contract, abstention, and invented IDs.
- Configuration without secrets and separate cost accounting.

Run: `python -m pytest -q`.

## Live validation

Live validation requires `.env`, available credit, and access to both models. Run
`python -m src.cli build-index` first, then representative queries. Public results are sanitized,
and the demo retains reproducible offline samples to avoid publishing credentials or depending on
external services.

Live validation performed on 16 August 2026:

- 37 chunks indexed with `text-embedding-3-small`.
- 7,119 embedding tokens and an estimated cost of USD 0.00014238.
- UC-03 retrieved `BUG-TRF-001`, `TC-TRF-004`, and `TC-TRF-007`; the response passed ID validation.
- The out-of-domain cultivation query returned an abstention and zero chunks.
- CI on `main` and the GitHub Pages deployment completed successfully.
- Public demo: <https://lucasvacis87.github.io/qa-memory-rag/>.

### LangChain migration — 17 August 2026

- Environment recreated with Python 3.13 and dependencies verified with `pip check`.
- Complete offline suite: 29 tests passed without network calls.
- Verified versions: `langchain==1.3.14`, `langchain-openai==1.4.1`,
  `langchain-chroma==1.1.0`, `chromadb==1.5.9`, and `openai==2.54.0`.
- Live indexing through `OpenAIEmbeddings` and `langchain-chroma`: 37 chunks with
  `text-embedding-3-small`, 7,119 tokens, and an estimated cost of USD 0.00014238.
- Live querying through `ChatPromptTemplate`, `ChatOpenAI`, the Responses API, and Structured
  Outputs retrieved `BUG-TRF-001`, `TC-TRF-004`, and `TC-TRF-007` as primary evidence.
- Query evaluation: 10/10, valid IDs, expected evidence present, and a JSON contract limited to
  `user_question`, `system_answer`, and `chunks_related`.
