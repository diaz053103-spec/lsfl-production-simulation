#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEALTH_CHECK = ROOT / "monitoring" / "health_check.sh"
ENGINE = ROOT / "automation" / "ticketing" / "incident_engine.py"
TICKETS = ROOT / "automation" / "ticketing" / "tickets.json"


def main():
    parser = argparse.ArgumentParser(description="LSFL health monitor and incident integration")
    parser.add_argument("--simulate-failure", action="store_true",
                        help="Simulate HTTP 000 without taking the portal offline")
    args = parser.parse_args()

    if args.simulate_failure:
        command = ["bash", "-c", 'curl() { printf "000"; }; source "$1"', "_", str(HEALTH_CHECK)]
    else:
        command = ["bash", str(HEALTH_CHECK)]

    result = subprocess.run(command, capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    if output:
        print(output)

    if result.returncode == 0:
        print("Monitor result: HEALTHY; no incident needed.")
        return 0

    tickets = json.loads(TICKETS.read_text())
    existing = next((t for t in tickets
                     if t.get("type") == "health_check_failure"
                     and t.get("status") not in ("RESOLVED", "CLOSED")), None)
    if existing:
        print(f"Duplicate avoided: reusing open incident {existing['id']}.")
        return 1

    before = {t["id"] for t in tickets}
    created = subprocess.run(
        [sys.executable, str(ENGINE), "--issue", "health_check_failure"],
        capture_output=True, text=True
    )
    if created.stdout:
        print(created.stdout.strip())
    if created.returncode:
        print(created.stderr.strip() or "ERROR: Incident creation failed.")
        return created.returncode

    tickets = json.loads(TICKETS.read_text())
    new_tickets = [t for t in tickets if t["id"] not in before]
    if len(new_tickets) != 1:
        print("ERROR: Could not uniquely identify the created incident.")
        return 2

    ticket = new_tickets[0]
    ticket["detection_source"] = "Automated Health Monitor"
    ticket["timeline"].append({
        "timestamp": ticket["detected_at"],
        "event": "Automatically created after a failed health check."
    })
    TICKETS.write_text(json.dumps(tickets, indent=2) + "\n")
    print(f"PASS: Automated incident created: {ticket['id']}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
