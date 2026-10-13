# Lone Star Fulfillment & Logistics (LSFL)

## Production Operations Simulation

LSFL demonstrates Docker containerization, health monitoring, automated incident ticketing, failure injection, and service recovery.

## Start the application
```bash
docker compose up -d --build
```

Open http://localhost:8080 to access the customer portal.

## Health checks
```bash
./monitoring/health_check.sh
./monitoring/system_health.sh
python3 monitoring/health_monitor.py
```

## Incident management
```bash
python3 automation/ticketing/incident_engine.py --list
python3 automation/ticketing/incident_engine.py --help
```

## Failure injection
```bash
python3 automation/failures/failure_injector.py --help
```

Failure injection may interrupt the portal. Recover it with `docker compose up -d` and verify with `./monitoring/health_check.sh`.

## Documentation
See `docs/`, `runbooks/`, `postmortems/`, and `automation/ticketing/README.md`.
