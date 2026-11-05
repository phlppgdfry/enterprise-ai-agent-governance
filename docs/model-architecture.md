# Bounded policy model experiment

The deterministic `agent.py` remains unchanged. `llm_agent.py` adds a `Provider`
protocol and a fixed-loopback Ollama implementation. No paid API is required.
An installed model must be selected explicitly; model weights are not redistributed.

1. Validate question length and CLI persona. This persona is a fixture, not login.
2. Handle obvious private-record requests, direct overrides and consequential decisions
   before inference. Regex catches examples only; it is not the primary security boundary.
3. Filter published documents by persona before assembling context. The complete three
   or four approved excerpts fit in a small context; a vector database would add no
   demonstrated benefit. Model selection over curated excerpts is not vector RAG.
The excerpts are reviewed summaries in `knowledge/policies.json`, not literal quotes
from the linked Markdown documents. The citation identifies the supporting policy;
exact validation is against the curated summary, not a verbatim span in that document.

4. Request a structured evidence proposal from the real model. Prompt is versioned;
   context is hashed. Bounded input, output, timeout and fixed destination constrain cost.
5. Validate exact schema, allowed source and complete verbatim excerpt. Unknown fields,
   tool proposals, altered quotes, truncated output and transport failures escalate.
6. Return the validated repository excerpt and source citation. No free-form model prose
   or raw provider error is returned. Correct attribution still permits an irrelevant
   allowed excerpt: the evaluation measures that failure separately.

## Permission boundaries

The model receives no action tools, tokens or endpoint-selection permission. `agent.py
submit` is a distinct explicitly confirmed employee action to the .NET API. There is no
approval tool. The API controls owner, role and decision version. New provider adapters
must preserve response limits, timeout, error redaction and schema validation.

The knowledge corpus is trusted, code-reviewed repository content. This implementation
does not ingest arbitrary documents. If a malicious instruction were published as the
actual policy excerpt, exact-copy validation could return it as content. Source review,
publication ownership and adversarial source-ingestion tests are required before remote
content ingestion. Do not treat prompt text or source hashes as authorization.

## Observability and operations

Each answer returns stage names, selected context IDs, prompt version, context hash,
provider/model, local elapsed time and provider token counts. It omits the question,
credentials and raw failures from the trace. Evaluation reports intentionally contain
synthetic questions and answers. No remote telemetry is configured. A consumer that
persists traces must add access controls, redaction and retention. Hashes do not make
logs anonymous. Model costs remain unknown rather than reported as free.

## Why no MCP or orchestration framework?

There is one existing fixed local HTTP submission function. It gains little from dynamic
tool discovery or a separate protocol server. Adding MCP would add another authority,
transport and deployment surface without a second consuming client. Reconsider when
several clients need a shared independently authorised tool service. Native Python and
one provider protocol make the boundary easier to test today. This is a scoped design
judgment, not a claim that MCP is universally inappropriate.

## Release decision

See [recorded failures and metrics](../eval/REPORT.md). Do not release the model experiment
until independently reviewed supported-question quality and tenant security gates pass.
Set `OLLAMA_MODEL=qwen3:8b` or use `--model qwen3:8b` to reproduce the better recorded run;
the smaller default demonstrates that a model being available does not make it suitable.

Official API reference checked with Context7 on 29 October 2026:
[Ollama chat, structured output and usage](https://github.com/ollama/ollama/blob/main/docs/api.md).
