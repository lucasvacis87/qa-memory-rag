# Architecture

```text
faq_document.txt -> parser/validation -> complete chunks -> LangChain OpenAIEmbeddings
       -> langchain-chroma -> ChromaDB collection (cosine)
       -> bug search + test_case search -> retrieved context
       -> ChatPromptTemplate -> ChatOpenAI/Responses API/Structured Outputs
       -> deterministic validation -> JSON
```

## Decisions

- One complete QA record maps to one chunk, preserving its ID, steps, relationships, and metadata.
- LangChain `OpenAIEmbeddings` uses `text-embedding-3-small`; ChromaDB persists vectors through
  `langchain-chroma` and uses cosine distance.
- Searches are filtered by `bug` and `test_case`, returning up to two records of each type.
- `ChatPromptTemplate` assembles instructions, the question, and retrieved evidence.
- `ChatOpenAI` explicitly uses the Responses API and `gpt-5.4-nano`; Structured Outputs requires
  the internal `system_answer` field before the public contract is built.
- A post-generation validation rejects every ID that does not belong to a retrieved chunk.
- Tests inject deterministic `Embeddings` and `Runnable` implementations to validate the flow
  without network access or cost.

LangChain orchestrates integrations; it does not determine whether an answer is supported. The
threshold, type separation, ID validation, abstention, and final JSON remain deterministic project
rules.

## Public contract

The response contains exactly `user_question`, `system_answer`, and `chunks_related`. Technical
metadata lives within each chunk; it neither changes filters nor adds top-level keys.

## Safe failures

- Missing configuration or index: operational error to `stderr` and a non-zero exit code.
- No evidence above the threshold: abstain without invoking the generator.
- Model-invented ID: replace the response with an abstention.
- Network, quota, or model error: never silently switch provider or model.
