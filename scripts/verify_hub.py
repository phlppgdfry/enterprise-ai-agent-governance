"""Optional real agent-to-Hub integration. Clone and build the sibling Hub first."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent import Agent, submit_request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hub", type=Path, default=Path("../enterprise-ai-automation-hub"))
    args = parser.parse_args()
    dll = args.hub.resolve() / "src/bin/Release/net10.0/AutomationHub.dll"
    if not dll.exists():
        parser.error("Build the sibling Hub in Release first")
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", 5088)) == 0:
            parser.error("Port 5088 is occupied; stop the other Hub before this isolated test")
    with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryFile() as log:
        process = subprocess.Popen(["dotnet", str(dll)], stdout=log, stderr=log,
            env=dict(os.environ, HUB_DATA=str(Path(temp) / "requests.json"), ASPNETCORE_ENVIRONMENT="Production"))
        try:
            for _ in range(100):
                if process.poll() is not None:
                    log.seek(0)
                    raise RuntimeError(log.read().decode())
                try:
                    with urllib.request.urlopen("http://127.0.0.1:5088/health", timeout=1):
                        break
                except OSError:
                    time.sleep(.1)
            else:
                raise RuntimeError("Hub did not start")
            assert Agent().answer("Ik wil een aanvraag indienen").outcome == "confirmation_required"
            first = submit_request("Integratie materiaal", "materials", 320,
                confirmed=True, token="demo-alice", idempotency_key="stack-demo")
            retry = submit_request("Integratie materiaal", "materials", 320,
                confirmed=True, token="demo-alice", idempotency_key="stack-demo")
            assert first["id"] == retry["id"] and first["status"] == "pending" and first["queue"] == "Finance"
            try:
                request = urllib.request.Request("http://127.0.0.1:5088/requests/" + first["id"],
                    headers={"Authorization": "Bearer demo-bob"})
                urllib.request.urlopen(request, timeout=5).close()
                raise AssertionError("Bob must not read Alice's request")
            except urllib.error.HTTPError as error:
                with error:
                    assert error.code == 404
            request = urllib.request.Request("http://127.0.0.1:5088/requests/" + first["id"] + "/decision",
                headers={"Content-Type": "application/json", "Authorization": "Bearer demo-manager"},
                data=json.dumps(dict(outcome="approved", reason="Integratietest menselijke beslissing", version=1)).encode())
            with urllib.request.urlopen(request, timeout=5) as response:
                decided = json.load(response)
            assert decided["status"] == "approved" and len(decided["events"]) == 2
            print(json.dumps(dict(mode="real-local-HTTP", confirmation="checked", retry="same ID",
                owner_isolation="404 for Bob", routing=decided["queue"], decision=decided["status"],
                actor=decided["events"][-1]["actor"]), indent=2))
        finally:
            process.terminate()
            process.wait(timeout=10)


if __name__ == "__main__":
    main()
