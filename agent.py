"""Auditable, deterministic reference agent. No LLM or Copilot calls are made.

The CLI role is a test fixture, never an authentication boundary. The API remains
authoritative for ownership and decisions. Knowledge documents are trusted code
assets; free-text retrieved instructions must never be executed.
"""
import argparse
from dataclasses import asdict, dataclass
import json
import math
from decimal import Decimal
import uuid
from pathlib import Path
import re
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
ROLES = {"employee", "approver"}


@dataclass(frozen=True)
class Answer:
    outcome: str
    text: str
    citations: tuple[str, ...] = ()
    tool: str | None = None


class Agent:
    def __init__(self, knowledge=None):
        self.knowledge = knowledge if knowledge is not None else json.loads(
            (ROOT / "knowledge/policies.json").read_text())

    def answer(self, question, role="employee"):
        if role not in ROLES:
            raise ValueError("Unknown role; authentication is required outside this simulator")
        if not isinstance(question, str) or not question.strip() or len(question) > 2000:
            raise ValueError("Question must have 1–2000 characters")
        text = question.casefold()
        # Illustrative defence in depth, NOT a complete prompt-injection detector.
        if re.search(r"ignore|negeer|system prompt|systeemprompt|bypass|omzeil|geheim|secret|vergeet.*regels", text):
            return Answer("refused", "Ik volg geen instructies om beveiliging of toegangsregels te omzeilen.")
        if re.search(r"salaris|loonstrook|salary|bankrekening|medisch|medical|diagnose|personeelsdossier", text):
            return Answer("refused", "Ik verwerk geen persoonlijke HR-dossiers. Neem contact op met HR.")
        if re.search(r"keur.*goed|\bapprove\b|goedkeuren|afkeuren|\breject\b|\bdecision\s+(?:approved|rejected)\b", text):
            return Answer("handoff", "Een bevoegde mens beslist in het goedkeuringsproces; de agent kan niet beslissen.")
        if re.search(r"aanvraag.*indienen|submit.*request", text):
            return Answer("confirmation_required", "Controleer categorie, omschrijving en bedrag; bevestig daarna expliciet de indiening.", tool="create_request")
        words = set(re.findall(r"\w+", text))
        # ACL filtering happens BEFORE matching; restricted content cannot influence an answer.
        allowed = [d for d in self.knowledge if d["published"] and role in d["roles"]]
        matches = []
        for document in allowed:
            score = len(words.intersection(document["keywords"]))
            if score:
                matches.append((score, document))
        if not matches:
            return Answer("abstain", "Ik vind hiervoor geen toegestane, gepubliceerde bron. Vraag de proceseigenaar om hulp.")
        best = max(score for score, _ in matches)
        winners = [d for score, d in matches if score == best]
        if len(winners) != 1:
            return Answer("clarify", "Over welk beleid gaat je vraag? Formuleer één onderwerp per vraag.")
        document = winners[0]
        return Answer("answered", document["answer"], (document["source"],))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Tool redirects are forbidden")


def open_local(request, timeout):
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect()).open(request, timeout=timeout)


def submit_request(title, category, amount, *, confirmed, token, idempotency_key,
                   base_url="http://127.0.0.1:5088"):
    """Call the sibling .NET Hub with the end user's demo identity.

    There is intentionally no decision tool and no maker/manager credential.
    Callers must retain the key across transport retries; do not auto-retry actions.
    """
    if confirmed is not True:
        raise ValueError("Explicit confirmation required")
    if token not in {"demo-alice", "demo-bob"}:
        raise ValueError("Use an employee demo identity")
    if not isinstance(title, str) or not title.strip() or len(title.strip()) > 160 or any(ord(c)<32 or ord(c)==127 for c in title):
        raise ValueError("Title must contain 1–160 printable characters")
    if category not in {"materials", "expense", "access"}:
        raise ValueError("Unknown category")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount) or not 0 <= amount <= 100000 or Decimal(str(amount)).as_tuple().exponent < -2 or (category == "access" and amount != 0):
        raise ValueError("Invalid request amount")
    if not isinstance(idempotency_key, str) or not idempotency_key.strip() or len(idempotency_key)>80 or any(ord(c)<32 or ord(c)==127 for c in idempotency_key):
        raise ValueError("Stable idempotency key required")
    parsed = urllib.parse.urlsplit(base_url)
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.port != 5088 or parsed.path not in ("", "/") or parsed.query or parsed.fragment or parsed.username:
        raise ValueError("Demo tools may only call the local Hub")
    request = urllib.request.Request(base_url.rstrip("/") + "/requests",
        data=json.dumps(dict(title=title, category=category, amount=amount)).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + token,
                 "Idempotency-Key": idempotency_key}, method="POST")
    with open_local(request, timeout=5) as response:
        raw = response.read(65537)
    if len(raw)>65536:
        raise ValueError("Tool response exceeds limit")
    result = json.loads(raw)
    if not isinstance(result, dict):
        raise ValueError("Unexpected Hub response")
    try:
        uuid.UUID(result["id"])
    except (KeyError,ValueError,TypeError,AttributeError):
        raise ValueError("Invalid Hub request ID") from None
    if result.get("owner") != token.removeprefix("demo-") or result.get("title") != title.strip() or result.get("category") != category or result.get("amount") != amount or result.get("status") not in {"pending","approved","rejected"}:
        raise ValueError("Hub response does not match the confirmed request")
    return result


def evaluate(path=ROOT / "eval/cases.json"):
    agent = Agent()
    cases = json.loads(Path(path).read_text())
    results = []
    for case in cases:
        answer = agent.answer(case["question"], case["role"])
        passed = (answer.outcome == case["outcome"] and list(answer.citations) == case["citations"]
                  and all(term.casefold() in answer.text.casefold() for term in case.get("must_contain", []))
                  and answer.tool == case.get("tool"))
        results.append(dict(id=case["id"], passed=passed, actual=asdict(answer)))
    return dict(mode="deterministic-reference", total=len(results),
                passed=sum(r["passed"] for r in results), results=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    ask = sub.add_parser("ask")
    ask.add_argument("question")
    ask.add_argument("--role", choices=sorted(ROLES), default="employee")
    evaluation = sub.add_parser("evaluate")
    evaluation.add_argument("--summary", action="store_true")
    submit = sub.add_parser("submit")
    submit.add_argument("--title", required=True)
    submit.add_argument("--category", choices=["materials", "expense", "access"], required=True)
    submit.add_argument("--amount", required=True, type=float)
    submit.add_argument("--identity", choices=["demo-alice", "demo-bob"], default="demo-alice")
    submit.add_argument("--key", required=True, help="Reuse this key for retries of the same request")
    submit.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "ask":
            result = asdict(Agent().answer(args.question, args.role))
        elif args.command == "evaluate":
            result = evaluate()
        else:
            result = submit_request(args.title, args.category, args.amount, confirmed=args.confirm,
                token=args.identity, idempotency_key=args.key)
    except (ValueError, OSError) as error:
        parser.exit(2, f"Error: {error}\n")
    output = {k: v for k, v in result.items() if k != "results"} if args.command == "evaluate" and args.summary else result
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if args.command == "evaluate" and result["passed"] != result["total"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
