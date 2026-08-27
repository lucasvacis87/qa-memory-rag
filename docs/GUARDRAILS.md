# Guardrails

## Data

- The knowledge base must be entirely fictional.
- Real banking data, personal data, credentials, internal tickets, and real incidents are prohibited.
- Query and response examples must retain that fictional nature.

## Evidence and answers

- The model may summarize and relate retrieved chunks, but it may not create evidence.
- It may not invent IDs, bugs, test cases, steps, expected results, or relationships.
- It must cite the IDs that support its recommendations.
- If retrieval does not provide sufficient evidence, it must explicitly abstain.
- Fictional technical metadata—functional domain, service or API, endpoint or operation, owning team, suggested smoke check, source, and validity—must be retained only when supported by the source.
- Each technical item or relationship must be marked `confirmed`, `partial`, or `unknown`. `Partial` does not allow missing data to be completed, and `unknown` is never replaced with an inference.
- A suggested smoke check must be labelled as such; it is neither a test case nor historical evidence unless the source explicitly records it.

## Secrets and costs

- The API key is stored only in `.env`, never in code, documentation, outputs, commits, or the web demo.
- `.env` and local indexes must be ignored by Git when they exist.
- Before creating a client or starting a network call, local configuration must validate the API key and models; errors go to `stderr` and exclude environment-variable values.
- Any credit purchase, paid-model change, or automatic-recharge activation requires explicit approval.
- Official pricing and availability must be checked again before buying credit.

## Technical boundaries

- One source document and one Chroma collection.
- Two simple filters: `bug` and `test_case`.
- Technical metadata remains inside `chunks_related` items; it adds no technical filters to the MVP and does not change the public contract.
- No SQL, Docker, public backend, authentication, multiple agents, or premature abstractions.
- The static demo must not contain an API key, backend, or OpenAI calls.
- No external connectors are included: the deliverable uses only the versioned local document.

## Minimum quality

- The public contract contains exactly three keys: `user_question`, `system_answer`, and `chunks_related`.
- Operational errors must go to `stderr` without exposing secrets.
- Changes to the source, retrieval, model, or format require updates to relevant documentation and tests.
