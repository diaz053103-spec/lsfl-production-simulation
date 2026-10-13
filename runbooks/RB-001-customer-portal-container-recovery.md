# Runbook: Customer Portal Container Recovery

## Runbook Information

- Runbook ID: RB-001
- Title: Customer Portal Container Recovery
- Service: LSFL Customer Portal
- Severity: SEV-2
- Owner: Operations
- Last Updated: 2026-10-13

## Purpose

Restore the LSFL Customer Portal when its Docker container is stopped or the portal is unavailable.

## Symptoms

- The portal at `http://localhost:8080` cannot be reached.
- The health check reports `UNHEALTHY` or HTTP 000.
- `docker compose ps -a` shows `lsfl-customer-portal` as exited.
- Customers cannot access the portal.

## Prerequisites

- Run commands from the root of the `lsfl-production-simulation` repository.
- Docker Desktop or the Docker daemon must be running.
- Docker Compose must be available.
- Record the incident ID before changing service state.

## Initial Checks

### 1. Check the Application

```bash
curl -sS -o /dev/null -w 'HTTP %{http_code}\n' --max-time 5 http://localhost:8080
```

Expected healthy result: `HTTP 200`.

### 2. Check the Container

```bash
docker compose ps -a
docker inspect lsfl-customer-portal \
  --format 'Status={{.State.Status}} ExitCode={{.State.ExitCode}}'
```

Check whether the container is running, exited, or unhealthy. An exit code of 0 can indicate a clean stop; it does not by itself prove why the service stopped.

### 3. Check Recent Logs

```bash
docker logs --tail 50 lsfl-customer-portal
```

Review the logs before recovery and record relevant evidence in the incident timeline.

### 4. Run the Health Check

```bash
bash monitoring/health_check.sh
```

Expected healthy result: `LSFL Customer Portal: HEALTHY (HTTP 200)`.

## Recovery Procedure

### 1. If the Container Is Stopped

Start the existing Compose service:

```bash
docker compose start web
```

If the container does not exist, inspect the Compose configuration and use `docker compose up -d --build web` only after confirming the intended configuration.

### 2. Verify Container State

```bash
docker compose ps
```

Wait for the container health status to become healthy. If it does not, inspect `docker logs --tail 50 lsfl-customer-portal` and investigate rather than repeatedly restarting it.

### 3. Verify the Portal

```bash
curl -sS -o /dev/null -w 'HTTP %{http_code}\n' --max-time 5 http://localhost:8080
bash monitoring/health_check.sh
```

Do not declare recovery until the portal returns HTTP 200 and the health check reports HEALTHY.

## Incident Ticket Updates

Replace `INC-XXXX` below with the actual incident ID:

```bash
python3 automation/ticketing/incident_engine.py --timeline INC-XXXX "Investigation: recorded container state and reviewed recent logs."
python3 automation/ticketing/incident_engine.py --timeline INC-XXXX "Recovery: started the customer portal container and verified HTTP 200 plus healthy container status."
```

Update the ticket to RESOLVED only after successful verification:

```bash
python3 automation/ticketing/incident_engine.py --update INC-XXXX RESOLVED
```

## Escalation

If the container will not start, the health check remains unhealthy, or the portal does not return HTTP 200:

1. Do not mark the incident resolved.
2. Capture `docker compose ps -a`, `docker inspect`, and recent container logs.
3. Check Docker daemon health and Compose configuration.
4. Continue investigation or escalate to the service owner.

## Recovery Criteria

- Container is running and healthy.
- Portal returns HTTP 200.
- Health-check script reports HEALTHY.
- Incident timeline contains investigation and recovery evidence.

## Related Files

- `monitoring/health_check.sh`
- `monitoring/system_health.sh`
- `automation/failures/failure_injector.py`
- `automation/ticketing/incident_engine.py`
- `postmortems/INC-1004-customer-portal-container-failure.md`
