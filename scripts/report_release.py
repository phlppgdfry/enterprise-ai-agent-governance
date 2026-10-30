"""Generate truthful release evaluation comparisons and per-failure analysis."""
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
lines=['# Release model evaluation — 30 October 2026','',
'**Both selectors remain EXPERIMENTAL.** Gates were frozen before implementation and the holdout was not tuned after observation.',
'The authored 32-case holdout is new regression material, not independently human-authored or production validation.',
'Historical 29 October reports remain unchanged under `eval/results/`. New runs use the same installed Qwen 8B model.','',
'| Run | Overall | Supported policy | Other cases | Model-call cases | Gate |',
'|---|---|---|---|---|---|']
reports=[]
for file in sorted((ROOT/'eval/release-results').glob('*.json')):
    r=json.loads(file.read_text());reports.append((file,r));s=r['supported'];others=[x for x in r['results'] if x['expected_outcome']!='answered']
    lines.append(f"| {file.stem} | {r['passed']}/{r['total']} | {s['passed']}/{s['total']} | {sum(x['passed'] for x in others)}/{len(others)} | {r['model_calls']} | FAIL |")
lines+=['','## What changed and what the results mean','',
'V1 requires a complete exact curated summary plus source ID. Recorded misses had the relevant source in context: retrieval absence is not supported as a root cause. Cross-language paraphrases, conservative abstention/clarification and exact-copy output burden are plausible contributors, not proven causal explanations.',
'V2 chooses a source ID from a persona-filtered catalog with bilingual topic descriptions; code renders the reviewed text. It improves supported-question selection but is too willing to choose a nearby allowed policy for unsupported, restricted-topic or forged-command questions. Compound-topic clarification also fails. These are coverage/relevance and instruction-following errors, not successful action execution.',
'No model action tools are exposed. No model-selected URL is used. All answered text still comes from allowed published summaries; a wrong safe-source answer is not a leak of the filtered reviewer document. The recorded `zero_unauthorized_evidence` gate is conservative: it flags an answer to a forbidden request, even if that answer contains only allowed evidence. It must not be reported as a demonstrated cross-persona content leak.',
'The Wilson 95% interval for 12/12 supported cases is [0.7575, 1.0]; for 4/12 it is [0.1381, 0.6094]. This small authored set cannot establish production accuracy. Pre-model refusals, handoffs and confirmations do not measure model reasoning.',
'Token counts, local latency, model/version, dataset hash and per-answer stages are in the JSON. Costs remain unknown. Correlation IDs are local trace identifiers, not distributed tracing. Raw model reasoning is not logged.','',
'## Failure-by-failure analysis','',
'Each row links the expected evidence and actual source/outcome. Tool calls are always none. Source documents are public synthetic fixtures; CLI roles are not authentication.','',
'| Run / case | Question | Expected | Actual | Classification / evidence |',
'|---|---|---|---|---|']
def clean(text):return str(text).replace('|','/').replace('\n',' ')
for file,r in reports:
    dataset=ROOT/('eval/model-cases.json' if 'legacy' in file.name else 'eval/holdout-v1.json')
    cases={c['id']:c for c in json.loads(dataset.read_text())}
    for x in r['results']:
        if x['passed']:continue
        c=cases[x['id']];actual=x['actual']
        category=('Provider/schema/exact-copy failure; v1 trace cannot distinguish further' if actual['outcome']=='escalate' else
                  'Supported evidence present; unnecessary non-answer' if x['expected_outcome']=='answered' else
                  'Ambiguous multi-topic request silently narrowed' if x['expected_outcome']=='clarify' else
                  'Unsupported/forged-authority request mapped to irrelevant allowed evidence')
        lines.append(f"| {file.stem}/{x['id']} | {clean(c['question'])} | {x['expected_outcome']}: {x['expected_source'] or 'no source'} | {actual['outcome']}: {', '.join(actual['citations']) or 'no source'} | {category}; tool calls: none |")
lines+=['','## Release decision','',
'Keep deterministic workflow controls as the demonstration default. Expose either model selector only as an explicit experiment with these failures visible. Next work: independently authored human-reviewed relevance/abstention cases and a separately versioned coverage validator. Do not tune on this holdout or lower the gates.',
'Action-tool selection: NOT APPLICABLE. Real Entra/source ACL, Microsoft execution and independent user validation: NOT EXECUTED.','']
content='\n'.join(lines)
path=ROOT/'eval/RELEASE_REPORT.md'
if args.check:
    if not path.exists() or path.read_text()!=content:raise SystemExit('Stale release evaluation report')
else:path.write_text(content)
print('Release model report '+('current' if args.check else 'generated'))
