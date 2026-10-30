# Verification record — 29 October 2026

Environment: macOS, Python 3.14.10, Ollama 0.40.11. Synthetic public policy corpus.
No paid inference, Microsoft tenant evaluation or independent reviewer.

| Executed command | Result |
|---|---|
| Initial `make verify` | 9 tests + deterministic 30/30 + docs passed |
| Updated `make verify` | 17 model-independent tests + deterministic 30/30 + generated-report and docs checks passed |
| `python3 scripts/evaluate_model.py --model qwen3:1.7b` | Exit 1: 7/12 overall; 0/4 supported; eight actual model calls |
| `python3 scripts/evaluate_model.py --model qwen3:8b --output eval/results/qwen3-8b.json` | Exit 1: 10/12 overall; 2/4 supported; eight actual model calls |
| `python3 scripts/report_model.py --check` | Generated Markdown/SVG consistent with both recorded JSON reports |
| `python3 scripts/verify_hub.py` | Passed: explicit confirmation, Finance routing, same-ID retry, Bob 404, human Maria approval |
| Limited credential-pattern scan | 0 findings in 39 text files at scan time; not comprehensive secret assurance |

Both model runs use the same prompt version and dataset hash. Four safety cases never
call the model. No action tools are exposed, so zero action invocations is a boundary
property, not model tool-selection accuracy. Cost is unknown; local measured tokens
and elapsed time are in each real report. No invented cloud cost or model-quality pass.

Tests cover filtered context, invalid personas, forged citations, altered curated
summaries, unknown action fields, malformed JSON, provider timeout and truncation.
These fixtures exercise code boundaries, not real model robustness. Curated summaries
are reviewed JSON policy answers; exact validation does not claim they are verbatim
spans in the supporting Markdown policy documents.

Release result: experimental only, quality gate unmet. Real authentication, remote
source access, tenant evaluation, independent holdout and human relevance review remain.
