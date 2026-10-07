#!/usr/bin/env python3

import argparse
import json
from datetime import datetime
from pathlib import Path
import random


BASE_DIR = Path(__file__).resolve().parent
CATALOG_FILE = BASE_DIR / "incidents.json"
TICKET_FILE = BASE_DIR / "tickets.json"

VALID_STATUSES = [
    "OPEN",
    "INVESTIGATING",
    "MITIGATED",
    "RESOLVED",
    "CLOSED"
]


def current_time():
    return datetime.now().astimezone().isoformat()


def load_catalog():
    with open(CATALOG_FILE, "r") as file:
        return json.load(file)


def load_tickets():
    if not TICKET_FILE.exists():
        return []

    with open(TICKET_FILE, "r") as file:
        return json.load(file)


def save_tickets(tickets):
    with open(TICKET_FILE, "w") as file:
        json.dump(tickets, file, indent=2)


def generate_incident_id(tickets):
    if not tickets:
        return "INC-1001"

    highest_number = max(
        int(ticket["id"].split("-")[1])
        for ticket in tickets
    )

    return f"INC-{highest_number + 1}"


def find_ticket(tickets, incident_id):
    for ticket in tickets:
        if ticket["id"] == incident_id:
            return ticket

    return None


def create_incident(issue_type=None):
    catalog = load_catalog()
    tickets = load_tickets()

    if issue_type:
        matches = [
            issue for issue in catalog
            if issue["type"] == issue_type
        ]

        if not matches:
            print(f"Unknown incident type: {issue_type}")
            print("\nAvailable incident types:")

            for issue in catalog:
                print(f"  - {issue['type']}")

            return

        issue = matches[0]

    else:
        issue = random.choice(catalog)

    timestamp = current_time()

    incident = {
        "id": generate_incident_id(tickets),
        "title": issue["title"],
        "type": issue["type"],
        "service": issue["service"],
        "severity": issue["severity"],
        "status": "OPEN",
        "detected_at": timestamp,
        "detection_source": "Incident Simulator",
        "symptoms": issue["symptoms"],
        "timeline": [
            {
                "timestamp": timestamp,
                "event": "Incident created"
            }
        ],
        "root_cause": None,
        "remediation": None,
        "resolved_at": None
    }

    tickets.append(incident)
    save_tickets(tickets)

    display_ticket(incident)


def display_ticket(ticket):
    print()
    print("=" * 60)
    print("LSFL INCIDENT")
    print("=" * 60)
    print(f"Incident ID:     {ticket['id']}")
    print(f"Title:           {ticket['title']}")
    print(f"Service:         {ticket['service']}")
    print(f"Severity:        {ticket['severity']}")
    print(f"Status:          {ticket['status']}")
    print(f"Detected:        {ticket['detected_at']}")
    print(f"Detection:       {ticket['detection_source']}")

    print()
    print("Symptoms:")

    for symptom in ticket["symptoms"]:
        print(f"  - {symptom}")

    print()
    print("Timeline:")

    for event in ticket["timeline"]:
        print(f"  {event['timestamp']}  {event['event']}")

    if ticket["root_cause"]:
        print()
        print(f"Root Cause:      {ticket['root_cause']}")

    if ticket["remediation"]:
        print(f"Remediation:     {ticket['remediation']}")

    print("=" * 60)
    print()


def list_incidents():
    tickets = load_tickets()

    if not tickets:
        print("No incidents found.")
        return

    print()
    print("=" * 90)
    print("LSFL INCIDENT QUEUE")
    print("=" * 90)

    print(
        f"{'ID':<12}"
        f"{'SEVERITY':<10}"
        f"{'STATUS':<16}"
        f"{'SERVICE':<22}"
        f"TITLE"
    )

    print("-" * 90)

    for ticket in tickets:
        print(
            f"{ticket['id']:<12}"
            f"{ticket['severity']:<10}"
            f"{ticket['status']:<16}"
            f"{ticket['service']:<22}"
            f"{ticket['title']}"
        )

    print("=" * 90)
    print()


def show_incident(incident_id):
    tickets = load_tickets()
    ticket = find_ticket(tickets, incident_id)

    if not ticket:
        print(f"Incident not found: {incident_id}")
        return

    display_ticket(ticket)


def update_status(incident_id, new_status):
    tickets = load_tickets()
    ticket = find_ticket(tickets, incident_id)

    if not ticket:
        print(f"Incident not found: {incident_id}")
        return

    if new_status not in VALID_STATUSES:
        print(f"Invalid status: {new_status}")
        print("Valid statuses:")
        print("  " + ", ".join(VALID_STATUSES))
        return

    old_status = ticket["status"]
    timestamp = current_time()

    ticket["status"] = new_status

    ticket["timeline"].append(
        {
            "timestamp": timestamp,
            "event": f"Status changed: {old_status} -> {new_status}"
        }
    )

    if new_status == "RESOLVED":
        ticket["resolved_at"] = timestamp

    save_tickets(tickets)

    print()
    print(
        f"{ticket['id']} updated: "
        f"{old_status} -> {new_status}"
    )
    print()


def add_timeline_event(incident_id, event):
    tickets = load_tickets()
    ticket = find_ticket(tickets, incident_id)

    if not ticket:
        print(f"Incident not found: {incident_id}")
        return

    timestamp = current_time()

    ticket["timeline"].append(
        {
            "timestamp": timestamp,
            "event": event
        }
    )

    save_tickets(tickets)

    print(f"Timeline updated for {incident_id}.")


def main():
    parser = argparse.ArgumentParser(
        description="LSFL Incident Management Engine"
    )

    parser.add_argument(
        "--random",
        action="store_true",
        help="Create a random incident"
    )

    parser.add_argument(
        "--issue",
        help="Create a specific incident type"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all incidents"
    )

    parser.add_argument(
        "--show",
        metavar="INCIDENT_ID",
        help="Show a specific incident"
    )

    parser.add_argument(
        "--update",
        nargs=2,
        metavar=("INCIDENT_ID", "STATUS"),
        help="Update incident status"
    )

    parser.add_argument(
        "--timeline",
        nargs=2,
        metavar=("INCIDENT_ID", "EVENT"),
        help="Add an investigation timeline event"
    )

    args = parser.parse_args()

    if args.random:
        create_incident()

    elif args.issue:
        create_incident(args.issue)

    elif args.list:
        list_incidents()

    elif args.show:
        show_incident(args.show)

    elif args.update:
        incident_id, new_status = args.update
        update_status(incident_id, new_status)

    elif args.timeline:
        incident_id, event = args.timeline
        add_timeline_event(incident_id, event)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
