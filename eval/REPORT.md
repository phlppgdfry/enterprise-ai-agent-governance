# Local model evaluation report

Executed on 29 October 2026 against Ollama 0.40.11 on macOS. All documents and questions are synthetic.
The prompt and dataset are unchanged between models. Reports retain unsuccessful outcomes; no failed cases were removed.

| Model | All cases | Model-call cases | Supported policy questions | Unauthorized citations | Input / output tokens | Max latency |
|---|---|---|---|---|---|---|
| qwen3:1.7b | 7/12 | 3/8 | 0/4 | 0 | 2880 / 176 | 8839 ms |
| qwen3:8b | 10/12 | 6/8 | 2/4 | 0 | 2880 / 251 | 7096 ms |

## Decision and limitations

**Do not release the model path to a business pilot.** The proposed 90% supported-question gate is unmet.
The deterministic reference remains the reproducible default. The real-model path is an inspectable experiment.
Qwen 8B correctly selected expense and materials evidence but missed software-permission and reviewer-follow-up paraphrases.
Qwen 1.7B missed all four supported questions. Abstention avoids fabrication but does not complete the task.

- Task completion: exact expected outcome and source, authored 12-case regression set.
- Attribution: server validates a whole exact excerpt and allowed source. This constrains generated text; it does not prove semantic relevance.
- Disclosure: zero unauthorized citations in this small corpus; all source files are public fixtures. This is not a tenant confidentiality test.
- Injection: direct override is pre-model gated; forged authority questions reach the model. Tests do not establish general injection resistance.
- Refusal and handoff: four cases are handled before inference and must not inflate claims about model safety.
- Tool selection: not applicable to this model path. Zero action tools are exposed; no autonomous tool invocation is attempted.
- Latency: trace values include local model loading and orchestration. Hardware, concurrency and cold starts affect repeatability.
- Costs: token counts are measured; EUR cost is unknown. Local hardware/electricity and cloud pricing are not inferred.
- Personas: CLI role selection is simulated. A real service needs validated identity before document filtering.
- Holdout: no independent reviewer, blinded human quality assessment or production traffic; future holdout must be created before prompt tuning.

## Reproduce

```bash
python3 scripts/evaluate_model.py --model qwen3:1.7b --output /tmp/qwen-small.json
python3 scripts/evaluate_model.py --model qwen3:8b --output /tmp/qwen-large.json
python3 scripts/report_model.py --check
```

The evaluation exits nonzero on a failed case. This is the expected recorded gate failure, not a passing model evaluation.
Raw per-case answers, source IDs, prompt/context fingerprints, tokens and stages are in `eval/results/`.
