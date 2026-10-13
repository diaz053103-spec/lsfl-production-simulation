# Incident Postmortem: INC-1004

## Incident Summary

- Incident ID: INC-1004
- Title: Customer Portal Container Failure
- Date: 2026-10-13
- Severity: SEV-2
- Duration: Exact duration not recorded; measure from outage start to successful recovery in future exercises.
- Service: Customer Portal
- Status: RESOLVED (confirm in incident ticket)

## Executive Summary

The LSFL Customer Portal became unavailable after the failure injector intentionally stopped the `lsfl-customer-portal` Docker container. Requests to port 8080 failed, returning HTTP 000, and the health check reported the service as unhealthy. The operations workflow investigated the container state and logs, restarted the service, and verified that the portal returned HTTP 200 and the container was healthy.

This was a controlled failure-injection exercise, not an unexpected production outage.

## Customer Impact

During the exercise, users could not connect to the customer portal at `http://localhost:8080`. Portal functions were unavailable while the container was stopped. No real customer impact was measured because this was a local simulation.

## Timeline

| Time (local, UTC-05:00) | Event |
|---|---|
| 17:12:49 | Incident INC-1004 created. |
| 17:13:01 | Incident moved to INVESTIGATING; baseline health was recorded. |
| 17:24:44 | Health check and curl confirmed the portal was unreachable (HTTP 000). |
| 17:24:44 | Docker inspection showed the container had exited with code 0. |
| After investigation | Container restarted using `docker compose start web`. |
| Recovery verification | Container reported healthy, portal returned HTTP 200, and health check reported HEALTHY. |

Note: The exact recovery timestamp was not recorded in the available output. The timeline should be updated if a precise duration is required.

## Technical Root Cause

### Primary Root Cause

The failure injector deliberately stopped the `lsfl-customer-portal` container, making the service unavailable on host port 8080.

### Contributing Factors

- The service depended on a single customer portal container.
- The container was stopped intentionally as part of the test.
- Detection was performed by manually running the health-check script; automated alert delivery was not demonstrated.

## Detection

The outage was detected by:
- A curl request to `http://localhost:8080` failing to connect and reporting HTTP 000.
- `monitoring/health_check.sh` reporting `UNHEALTHY (HTTP 000)`.
- `docker compose ps -a` showing the container as exited.

## Response

### Investigation

The operations workflow reviewed the incident queue, inspected the container state and exit code, and reviewed recent NGINX logs. The logs showed NGINX workers and the master process exiting, consistent with the intentional container stop.

### Mitigation

The container was restarted using:

```bash
docker compose start web
```

### Recovery

Recovery was confirmed by:
- `docker compose ps` showing the container running and healthy.
- curl returning HTTP 200 from `http://localhost:8080`.
- `monitoring/health_check.sh` reporting HEALTHY.

## What Went Well

1. The failure was reproduced in a controlled, repeatable way.
2. The health-check script clearly identified the unavailable portal.
3. Container inspection and logs supported the diagnosis, and recovery was verified.

## What Went Poorly

1. The exact outage duration was not captured.
2. Detection required an operator to run the health check manually.
3. The exercise did not demonstrate automated alert delivery or automatic incident creation.

## Corrective Actions

| Action | Owner | Priority | Status |
|---|---|---|---|
| Record detection and recovery timestamps for each exercise | Operations | Medium | Recommended |
| Run the portal health check on a schedule and route failures to an alert destination | Operations | High | Planned |
| Evaluate automated incident creation from monitoring alerts | Operations | Medium | Planned |

## Preventive Actions

1. Schedule health checks and retain their results.
2. Document a standard recovery procedure for a stopped portal container.
3. Add a smoke test to verify the portal after container recovery or deployment.

## Lessons Learned

### Technical Lessons

HTTP 000 indicates curl could not establish an HTTP connection. Docker's exited state and the container logs helped distinguish an intentional stop from an application-level HTTP error.

### Operational Lessons

Recovery should be verified at both the container and application levels. A running container alone does not prove the portal is serving requests correctly.

### Process Lessons

An incident record should capture the time of detection, mitigation, and recovery so service restoration time can be measured accurately.

## Final Assessment

The controlled failure and recovery were successful. The next improvements are scheduled detection, alert routing, more complete timestamps, and repeatable post-recovery smoke tests. The simulation does not currently prove automated alerting or automatic ticket creation.
