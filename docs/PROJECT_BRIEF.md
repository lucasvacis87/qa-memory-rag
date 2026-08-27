# Project brief

## Problem

In QA, finding prior incidents and deciding which regression coverage to run can require reviewing scattered tickets and test cases. QA Memory RAG reduces that manual search through a fictional, traceable, semantically searchable knowledge base.

## Objective

Accept a situation reported by a tester, retrieve similar historical bugs and related existing test cases, and return a recommendation grounded in that evidence.

The response must cite retrieved IDs. When evidence is insufficient, it must abstain rather than invent a recommendation.

## Users

- Manual testers investigating an incident or preparing a regression.
- QA Automation Engineers who need prior evidence to select existing coverage.
- Academic reviewers assessing the RAG flow, traceability, and JSON output.

## Fictional domain

The application represents a digital bank with six modules:

1. Authentication and account lockout.
2. Balances and transactions.
3. Transfers.
4. Bill payments.
5. Cards and limits.
6. Notifications and receipts.

## Use cases

| ID | Reported situation | Expected evidence | Expected outcome |
| --- | --- | --- | --- |
| UC-01 | The user is locked before the fifth attempt. | Authentication bug and test cases. | Explain the precedent and recommend attempt and unlock regression coverage. |
| UC-02 | An approved transfer does not appear in transactions. | Balance and history bug and test cases. | Relate the operation to history consistency. |
| UC-03 | A rejected transfer deducts the balance. | `BUG-TRF-001`, `TC-TRF-004`, and `TC-TRF-007`. | Identify the critical precedent and recommend rejection and reversal regression coverage. |
| UC-04 | A payment is duplicated after retrying. | Payment and idempotency bug and test cases. | Recommend verifying that only one debit exists. |
| UC-05 | A card limit changes in the UI but not in the backend. | Card bug and test cases. | Relate UI and backend controls. |
| UC-06 | A successful operation does not generate a receipt or notification. | Notification bug and test cases. | Recommend validating receipt issuance and display. |

Two cross-cutting behaviours are also validated:

- A query about a nonexistent capability must produce a clear abstention.
- A regression query must recommend only existing test cases, with their IDs.

## Scope

- One plain-text document: `data/faq_document.txt`.
- At least 15 fictional bugs, 20 test cases, and a functional introduction to the modules.
- A minimal *evidence-only* technical catalogue for fictional records: functional domain, service or API, endpoint or operation, owning team, suggested smoke check, source, and validity.
- Each technical item or relationship is marked `confirmed`, `partial`, or `unknown`: only what the source explicitly states is confirmed, and gaps are not filled by inference.
- One semantic chunk per bug or test case, with ID, type, module, and supported technical metadata.
- A local Chroma collection using cosine-similarity search.
- Two filtered searches: `bug` and `test_case`.
- Up to two bugs and two test cases per query.
- A JSON response containing exactly `user_question`, `system_answer`, and `chunks_related`.

The MVP keeps `bug` and `test_case` retrieval separate. Technical metadata adds no filters in this first version; it remains inside each `chunks_related` item so the response remains auditable without changing the public contract.

A suggested smoke check can only derive from retrieved evidence and must be labelled as a suggestion; it is not an existing test case or historical evidence. When that evidence is insufficient, the system must abstain.

## Technical decisions

| Decision | Choice | Rationale |
| --- | --- | --- |
| Language | Python 3.12 | Appropriate for the module and keeps the project accessible. |
| Embeddings | `text-embedding-3-small` | Reduces cost and meets the educational need. |
| Generation | A cost-efficient OpenAI model | Summarizes retrieved evidence without expanding scope. |
| Vector store | Local Chroma | Persists and reopens the index without external infrastructure. |
| Chunking | Per complete QA record | Preserves IDs, steps, results, and traceability. |
| Demo | Native HTML, CSS, and JavaScript | Can be statically published without backend or secrets. |

These decisions are implemented. The offline suite validates the complete flow without consumption;
the production path uses the models configured in `.env`.

## Out of scope

- Real data, real tickets, personal or banking information.
- Generation of new test cases or bugs.
- SQL database, Docker, authentication, public backend, or multiple agents.
- A frontend using React, Vite, npm, or direct OpenAI calls from the browser.
- Ticket-manager or external-source connectors.

## Success criteria

- The RAG retrieves relevant evidence for the six use cases.
- Recommendations mention only IDs present in the source.
- Technical relationships, owners, endpoints, and smoke checks are not invented and preserve their source, validity, and evidence state.
- Queries without evidence receive an abstention, not invented content.
- The project meets the brief: 20+ chunks, embeddings, vector search, JSON response, and reproducible documentation.
