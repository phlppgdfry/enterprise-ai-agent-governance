# Noordwerk portfolio release candidate — 30 October 2026

Status: local engineering complete within the reference-demo scope; hosted checks are
reported separately after actual execution. This is not a production release.

- Preserves deterministic defaults and every historical failed model report.
- Freezes a 32-case holdout and gates before selector v2; adds source-ID-only experiment and correlation traces.
- Same Qwen 8B: v1 4/12 supported and 22/32 overall; v2 12/12 supported but 21/32 overall. BOTH fail gates.
- Hardens confirmed local submission: rejects redirects, proxies, bad arguments, malformed/mismatched/oversize responses.
- Adds provider-envelope/failure tests, per-failure analysis, immutable CI pins and cross-repository integration workflow.
- CLI persona is not authentication; no action tools are exposed to the model.

Review: `make verify`; read `RELEASE_VERIFICATION.md`, inspect the full diff against
`origin/main`, then follow the central integrated demonstration in the consulting repo.
All new content is synthetic or authored. Visibility remains PUBLIC as independently
verified and explicitly authorized by the owner. Only feature-branch pushes and draft
PRs are authorized; no merge, main push, visibility change, release or deployment.
