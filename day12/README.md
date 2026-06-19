# Day 12 — Contextual Compression + Metadata Filtering

## Theory

Naive retrieval returns whole chunks (500-800 chars each) even when only 1-2 sentences
in each chunk actually answer the question. This wastes tokens and adds noise to the
LLM's context. **Contextual compression** fixes this by running each retrieved chunk
through an LLM (`LLMChainExtractor` pattern) that extracts only the sentences relevant
to the query, discarding the rest.

**Metadata filtering** solves a different problem: relevance ≠ correctness. Vector
search alone can't enforce hard constraints like "only search within category X" — it
just finds what's semantically similar. Filtering applies a `WHERE` clause on metadata
(`category`, `source`, `date`) *before* the similarity search runs, so irrelevant
documents are excluded outright instead of just ranked lower.

## Architecture

```
Query → embed → ChromaDB similarity search (with optional metadata filter)
      → top-k raw chunks → per-chunk LLM extraction (Gemini 2.5 Flash)
      → compressed chunks → final answer context
```

- `ingest.py` — loads PDFs, chunks text (500 chars), tags each chunk with
  `source`, `category`, `date` metadata, embeds via `gemini-embedding-001`,
  stores in ChromaDB (`day12_collection`).
- `compression_retriever.py` — `retrieve_and_compress()` does retrieval +
  filtering + compression in one call. `build_metadata_filter()` combines
  `category`/`source` filters with `$and` when both are given.
- `test_queries.py` — measures raw vs. compressed context size, and validates
  metadata filtering correctness on 2 fields.

## Results

### Compression

|            Query              | Raw chars | Compressed chars |
|-------------------------------|-----------|------------------|
| What is centralized database? |    2514   |        461       |
| What are tablet PC's?         |    2511   |        260       |

**Average reduction: 85.7%** across test queries — over 4/5 of the retrieved
context was irrelevant noise that compression stripped out before it ever
reached the final LLM call.

### Before/After example

**Question:** *What is centralized database?*

**BEFORE (raw chunk, 2514 chars total context):**
> Question: Explain the difference between Centralized database, Client/Server
> Database and Distributed database and give an example of each. Centralized
> Database: A centralized database is stored and maintained in a single
> location, usually a central computer or server. All users access this one
> ce[ntral database]...

**AFTER (compressed):**
> A centralized database is stored and maintained in a single location,
> usually a central computer or server. All users access this one central
> database through terminals or network connections.

The raw chunk included the question prompt itself (an artifact of how the PDF
was structured) plus surrounding unrelated text. Compression isolated just the
definition — proof the extraction step is doing real filtering, not just
truncating.

### Metadata filtering (2 fields tested)

```
[category=computers] PASS — returned only: {'computers'}
[category=databases, source=Types_of_database.pdf] PASS — returned only: {'Types_of_database.pdf'}
```

- **Field 1 (category only):** filtering to `category=computers` returned
  exclusively computer-category chunks — no leakage from the database PDF.
- **Field 2 (category + source combined via `$and`):** filtering to
  `category=databases` AND `source=Types_of_database.pdf` simultaneously
  returned only chunks matching both conditions.

## Conclusion

Compression cut context size by 85.7% on average without losing the answer —
fewer tokens sent to the final LLM, lower cost, less noise for the model to
filter through itself. Metadata filtering correctly enforces hard constraints
on 2 independent fields, confirming the retriever respects category/source
boundaries instead of relying on semantic similarity alone.