# LSFL Failure-Injection Evidence Matrix

Project: Lone Star Fulfillment & Logistics production simulation  
Environment: Local Docker Compose deployment  
Purpose: Record scenario coverage, observed behavior, and operational limits.

| Scenario | Expected signal or behavior | Evidence / verification |
|---|---|---|
| Container failure | Portal connection fails while the container is stopped; restart restores service | Verified: health check returned HTTP 000 during the outage and HTTP 200 after restart. See incident INC-1004 and its postmortem. |
| NGINX failure | NGINX configuration/service failure is investigated using configuration validation, logs, and HTTP checks | Limitation: the `nginx_failure` injector installs an invalid config but does not force an outage. Do not claim that this specific injector independently produced an outage. |
| Bad deployment | Faulty deployment returns HTTP 503; rollback restores service | PASS: recorded in `bad-deployment-test.md`; known-good config was restored and HTTP 200 verified. |
| High CPU | Bounded CPU workload runs and cleans up | PASS: recorded in `high-cpu-test.md`; workload lasted approximately 10 seconds and cleanup was verified. |
| High disk usage | Temporary disk test file is created and removed | Scenario is implemented as a bounded 32 MiB temporary-file workload. Record actual observed output when retaining detailed evidence; this test does not by itself prove host disk alerting. |
| Health-check failure | A failed health check is reported and the incident workflow is exercised | Verified: monitor reported HTTP 000 and reused existing open incident INC-1005 rather than creating a duplicate. |

## Important distinctions
- An injected fault, a detected fault, and an automatically created ticket are
  separate outcomes; document only the outcomes actually observed.
- The health-check simulation can report failure without stopping the portal.
- The container-failure test separately verified an actual connection failure
  and subsequent recovery.
- The bad-deployment scenario is the demonstrated HTTP 503 and rollback test.
- The separate NGINX failure injector has a known limitation and is not
  represented as a successfully activated outage.

## Evidence files
- `bad-deployment-test.md`
- `high-cpu-test.md`
- `../backups/default.conf`
- `../../postmortems/INC-1004-customer-portal-container-failure.md`
- `../../runbooks/RB-001-customer-portal-container-recovery.md`
