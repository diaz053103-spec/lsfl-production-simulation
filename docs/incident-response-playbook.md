# LSFL Incident Response Playbook

## 1. Detect and acknowledge
- Run `./monitoring/health_check.sh` for the customer portal.
- Run `docker compose ps` to inspect container state and health.
- Use `python3 monitoring/health_monitor.py` for monitor-driven detection.
- Capture the timestamp, HTTP result, affected service, and detection source.

## 2. Classify severity
- SEV-1: critical outage with major customer impact; immediate response.
- SEV-2: important service unavailable or significantly degraded; urgent response.
- SEV-3: limited impact or elevated host resource usage; normal operational priority.
- SEV-4: low-impact warning or maintenance issue; scheduled response.

Severity is a starting point. Reassess it using actual impact and scope.

## 3. Create or update the incident
Review existing tickets first:
`python3 automation/ticketing/incident_engine.py --list`

Inspect a related ticket:
`python3 automation/ticketing/incident_engine.py --show INC-1003`

Create an incident only when an appropriate record does not already exist:
`python3 automation/ticketing/incident_engine.py --issue container_failure`

Begin investigation:
`python3 automation/ticketing/incident_engine.py --update INC-1004 INVESTIGATING`

Record findings:
`python3 automation/ticketing/incident_engine.py --timeline INC-1004 "Container stopped; HTTP 000 confirmed"`

Use the actual incident ID for every command. The examples above illustrate
syntax; do not run them blindly against an incident whose current state differs.

## 4. Investigate by symptom

### Portal connection failure / HTTP 000
1. Run `docker compose ps`.
2. Inspect `docker logs lsfl-customer-portal`.
3. Check `./monitoring/health_check.sh`.
4. If the container is stopped, start it with `docker compose start web`.
5. Verify HTTP 200 and healthy container status.

### HTTP 502 or NGINX configuration problem
1. Inspect container status and logs.
2. Validate the active configuration with `docker exec lsfl-customer-portal nginx -t`.
3. Review recent configuration or deployment changes.
4. Restore a known-good configuration when required.
5. Validate the restored configuration, reload NGINX if appropriate, and verify HTTP 200.

Do not assume every NGINX failure produces HTTP 502. A stopped service may instead
produce a connection failure, while an active configuration can return HTTP 5xx.

### HTTP 503 after deployment
1. Capture the failed response and identify the changed configuration.
2. Follow the bad-deployment rollback procedure.
3. Verify the restored configuration with `nginx -t`.
4. Confirm the portal returns HTTP 200 after rollback.

### High CPU or disk usage
1. Inspect host/container resource usage and identify the process or workload.
2. Confirm whether the load is temporary or persistent.
3. Remove only test artifacts created by the simulation.
4. Repeat the resource check and record before/after results.

## 5. Mitigate, recover, and resolve
- Prefer a reversible, known-good recovery action.
- Record each action and its result in the incident timeline.
- Verify the customer-facing health check and container health.
- Record the root cause, remediation, and verification evidence.
- Mark RESOLVED only after recovery is demonstrated.
- Use CLOSED after required follow-up actions are complete.

## 6. Post-incident review
For significant simulated incidents, record:
- Impact and duration, distinguishing measured values from estimates.
- Detection method and response timeline.
- Confirmed root cause, or explicitly state that it remains unknown.
- Recovery steps and verification results.
- Preventive actions and remaining limitations.

These procedures describe a local simulation, not a live production on-call service.
