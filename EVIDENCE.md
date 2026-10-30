# Capability evidence matrix

Last verified: **29 October 2026**. Environment: macOS, Python 3.14, Ollama 0.40.11;
synthetic corpus and authored questions. No tenant or independent holdout evaluation.

| Capability / status | Implementation | Test method / result | Evidence artifact | Limitation |
|---|---|---|---|---|
| Deterministic reference — **Implemented and verified** | `agent.py` | 30/30 cases; original unit tests retained | `eval/cases.json`, `VERIFICATION.md` | Keyword reference, not model inference |
| Real LLM adapter — **Implemented and verified** | `llm_agent.py` provider protocol + Ollama | Two real runs, eight model calls each | `eval/results/`, `eval/REPORT.md` | Quality gate fails; local hardware dependent |
| Model task completion — **Implemented and verified, failed quality gate** | Model experiment | 1.7B: 7/12 total, 0/4 supported; 8B: 10/12 total, 2/4 supported | Per-case JSON and generated chart | Authored small set; safety cases are separate from model calls |
| Publication / persona filter — **Implemented and verified** | Context assembled after filtering | Stub provider sees no approver/draft content for employee | `tests/test_llm_agent.py` | Persona is a CLI fixture, corpus is public |
| Schema / citation / excerpt validation — **Implemented and verified** | Code outside model | Forged IDs, modified summaries, unknown action fields, invalid JSON rejected | `tests/test_llm_agent.py` | Exact curated summary match proves attribution, not relevance or a verbatim Markdown quote |
| Failure handling — **Implemented and verified** | Timeout/output validation | Provider timeout and truncation fixtures escalate safely | Boundary tests | Failure injection is simulated; no outage SLA |
| Decision authority boundary — **Implemented and verified** | No model action tools; separate confirmed submit | No network without confirmation; fixed destination and employee only | `tests/test_agent.py`, stack script | No model tool-selection accuracy claim |
| Trace / tokens / latency — **Implemented and verified** | Per-answer metadata | Recorded prompt/context hash, stages, provider counts and local time | Real-run JSON | Hardware cost unknown; no remote telemetry |
| Authentication — **Simulated** | `--role` | Persona tests only | `SECURITY.md` | Real authentication must precede ACL filtering |
| Copilot Studio / Entra / remote source ACL — **Documented design** | `copilot-studio/build-guide.md` | No tenant acceptance executed | Build guide, Hub handoff | Not an exportable or deployed agent |
| Cloud provider deployment — **Blocked by missing designated endpoint / credentials / entitlement** | Provider abstraction | No paid or cloud model call made | `docs/model-architecture.md` | Local model success is not Azure success |
| Independent holdout and human review — **Planned** | Release policy | Not executed | `governance/release-policy.md` | Required before release |
| HTTP submission to Hub — **Implemented but not externally verified** | Existing `submit_request` | Local .NET integration verified separately in final run | `scripts/verify_hub.py`, `VERIFICATION.md` | Loopback only, no Microsoft cloud connector |

“Implemented but not externally verified” distinguishes a verified local integration
from an untested external deployment. It never means an external run succeeded.

See [verification](VERIFICATION.md), [model failure analysis](eval/REPORT.md) and
[transformation report](TRANSFORMATION_REPORT.md) for exact commands and remaining work.

## Release candidate delta — 30 October 2026

The prior matrix is historical. [Release verification](RELEASE_VERIFICATION.md) records current pass/fail and unexecuted boundaries. [Release notes](RELEASE_NOTES.md) identify new implementation and preserved limitations. Hosted CI is recorded only after execution.
