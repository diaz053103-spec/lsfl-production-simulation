# LSFL Project 3 — System Architecture

This diagram describes the implemented production operations simulation.
Payment processing, inventory services, and a dedicated order-processing
backend are not implemented in this project.

```mermaid
flowchart TB
    USER["User / Browser"]
    WEB["NGINX Web Container"]
    UI["Customer Portal<br/>app/index.html"]
    API["Python Operations API<br/>Port 8000 internally"]
    TICKETS["JSON Ticket Records"]
    DOCS["Documentation and Runbooks"]
    HEALTH["Health Check Scripts"]
    ENGINE["Incident Engine"]
    INJECT["Failure Injection Scripts"]

    USER -->|"HTTP port 8080"| WEB
    WEB -->|"Serves portal"| UI
    WEB -->|"/api/* reverse proxy"| API
    API --> TICKETS
    API --> DOCS
    HEALTH -->|"Checks availability"| WEB
    ENGINE -->|"Creates and updates tickets"| TICKETS
    INJECT -->|"Simulates failures"| WEB
```

## Implemented Components

- NGINX serves the customer portal and proxies API requests.
- The Python API provides health, ticket, and documentation endpoints.
- Incident records are stored in JSON.
- Shell scripts check portal availability and Docker health.
- The incident engine creates and updates incident tickets.
- Failure-injection scripts simulate service failures for recovery testing.
- Documentation includes incident-response procedures, runbooks, postmortems,
  and failure evidence.

## API Endpoints

- `/api/health` — application health.
- `/api/tickets` — incident and ticket records.
- `/api/docs` — documentation index.

## Scope

This is an operations simulation, not a complete fulfillment platform.
Payment processing, inventory management, and a dedicated order-processing
service are not currently implemented.
