# LSFL Incident Ticketing Service

## Purpose
The incident engine records simulated production incidents in a persistent
JSON ticket queue. It supports incident creation, severity, status updates,
investigation timelines, and resolution timestamps.

## Files
- `incident_engine.py` — ticket lifecycle CLI.
- `incidents.json` — catalog of supported incident types and symptoms.
- `tickets.json` — incident records and investigation history.

## Commands
List the queue:
`python3 automation/ticketing/incident_engine.py --list`

Inspect a ticket:
`python3 automation/ticketing/incident_engine.py --show INC-1005`

Create a ticket from a catalog type:
`python3 automation/ticketing/incident_engine.py --issue health_check_failure`

Update a ticket:
`python3 automation/ticketing/incident_engine.py --update INC-1005 INVESTIGATING`

Record an investigation event:
`python3 automation/ticketing/incident_engine.py --timeline INC-1005 "Confirmed HTTP 000 during outage"`

Supported statuses: OPEN, INVESTIGATING, MITIGATED, RESOLVED, CLOSED.

## Operational rules
1. Review the queue before creating a ticket to avoid duplicates.
2. Record detection time, symptoms, and the detection source.
3. Move the ticket to INVESTIGATING and add timestamped findings.
4. Record root cause and remediation in the incident timeline.
5. Verify service recovery before marking the incident RESOLVED.
6. Close only after required follow-up work is complete.
7. Preserve incident history. Do not delete tickets to make the queue appear clean.

The current implementation stores root-cause and remediation fields, but
investigation events should also be added to the timeline. The engine does
not automatically deduplicate every incident type; duplicate avoidance
must be verified for the relevant detection path.

## Scope
This is a local production-operations simulation. It demonstrates ticket
lifecycle workflows and does not represent a production paging or on-call
platform.
