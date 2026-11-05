"""Summarise all recorded model runs, including failures. Does not call a model."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--check',action='store_true')
args=parser.parse_args()
runs=[json.loads(p.read_text()) for p in sorted((ROOT/'eval/results').glob('*.json'))]
lines=['# Local model evaluation report','',
'Executed on 29 October 2026 against Ollama 0.40.11 on macOS. All documents and questions are synthetic.',
'The prompt and dataset are unchanged between models. Reports retain unsuccessful outcomes; no failed cases were removed.','',
'| Model | All cases | Model-call cases | Supported policy questions | Unauthorized citations | Input / output tokens | Max latency |',
'|---|---|---|---|---|---|---|']
for run in runs:
    results=run['results'];called=[r for r in results if r['actual']['trace']['model_called']]
    supported=[r for r in results if r['expected_outcome']=='answered']
    score=lambda xs:f"{sum(x['passed'] for x in xs)}/{len(xs)}"
    lines.append(f"| {run['environment']['model']} | {score(results)} | {score(called)} | {score(supported)} | {run['unauthorized_citations']} | {run['input_tokens']} / {run['output_tokens']} | {run['latency_ms']['max']:.0f} ms |")
lines+=['','## Decision and limitations','',
'**Do not release the model path to a business pilot.** The proposed 90% supported-question gate is unmet.',
'The deterministic reference remains the reproducible default. The real-model path is an inspectable experiment.',
'Qwen 8B correctly selected expense and materials evidence but missed software-permission and reviewer-follow-up paraphrases.',
'Qwen 1.7B missed all four supported questions. Abstention avoids fabrication but does not complete the task.','',
'- Task completion: exact expected outcome and source, authored 12-case regression set.',
'- Attribution: server validates a whole exact excerpt and allowed source. This constrains generated text; it does not prove semantic relevance.',
'- Disclosure: zero unauthorized citations in this small corpus; all source files are public fixtures. This is not a tenant confidentiality test.',
'- Injection: direct override is pre-model gated; forged authority questions reach the model. Tests do not establish general injection resistance.',
'- Refusal and handoff: four cases are handled before inference and must not inflate claims about model safety.',
'- Tool selection: not applicable to this model path. Zero action tools are exposed; no autonomous tool invocation is attempted.',
'- Latency: trace values include local model loading and orchestration. Hardware, concurrency and cold starts affect repeatability.',
'- Costs: token counts are measured; EUR cost is unknown. Local hardware/electricity and cloud pricing are not inferred.',
'- Personas: CLI role selection is simulated. A real service needs validated identity before document filtering.',
'- Holdout: no independent reviewer, blinded human quality assessment or production traffic; future holdout must be created before prompt tuning.','',
'## Reproduce','',
'```bash',
'python3 scripts/evaluate_model.py --model qwen3:1.7b --output /tmp/qwen-small.json',
'python3 scripts/evaluate_model.py --model qwen3:8b --output /tmp/qwen-large.json',
'python3 scripts/report_model.py --check','```','',
'The evaluation exits nonzero on a failed case. This is the expected recorded gate failure, not a passing model evaluation.',
'Raw per-case answers, source IDs, prompt/context fingerprints, tokens and stages are in `eval/results/`.','']
report='\n'.join(lines)
# Accessible SVG data chart. Values derive only from committed real-run evidence.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="430" viewBox="0 0 1200 430" role="img" aria-labelledby="title desc">',
'<title id="title">Real local model evaluation: supported policy questions</title>',
'<desc id="desc">Qwen 1.7B answered zero of four supported questions correctly; Qwen 8B answered two of four. Both miss the 90 percent release gate. Authored synthetic cases, not production evaluation.</desc>',
'<rect width="1200" height="430" fill="#20384a"/>',
'<g font-family="Arial, sans-serif" fill="white">',
'<text x="55" y="68" font-size="18" fill="#addbcf">Noordwerk / Govern</text>',
'<text x="55" y="118" font-size="34" font-weight="bold">A source check is only part of answer quality.</text>',
'<text x="55" y="154" font-size="17" fill="#c1d2dc">Supported-question accuracy · Real local inference · 29 October 2026</text>']
for i,run in enumerate(runs):
    cases=[r for r in run['results'] if r['expected_outcome']=='answered'];passed=sum(r['passed'] for r in cases);y=214+i*72
    svg.append(f'<text x="55" y="{y+20}" font-size="19">{run["environment"]["model"]}</text><rect x="290" y="{y}" width="600" height="28" rx="3" fill="#436072"/><rect x="290" y="{y}" width="{600*passed/len(cases)}" height="28" rx="3" fill="#91d3bf"/><text x="920" y="{y+21}" font-size="21">{passed}/{len(cases)}</text>')
svg+=['<text x="55" y="392" font-size="16" fill="#f4d5a1">Release gate unmet. Small authored test set; CLI personas; no action tools; no tenant claims.</text></g></svg>']
outputs={ROOT/'eval/REPORT.md':report,ROOT/'docs/assets/model-evaluation.svg':'\n'.join(svg)+'\n'}
for path,content in outputs.items():
    if args.check:
        if not path.exists() or path.read_text()!=content:
            raise SystemExit(f'Stale generated evidence: {path.name}')
    else:
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)
print('Model evidence summaries: '+('current' if args.check else 'generated'))
