# LSFL Incident Management

## Severity Levels

### SEV-1 — Critical

Major production outage or severe customer impact.

Examples:

- Customer portal unavailable
- Order processing completely unavailable
- Critical production database failure
- Major security incident

Target response: Immediate.

### SEV-2 — High

Significant degradation affecting multiple users or an important production
service.

Examples:

- API returning elevated 5xx errors
- Inventory service unavailable
- Severe performance degradation

Target response: Urgent.

### SEV-3 — Moderate

Limited production impact or non-critical service degradation.

Examples:

- Internal dashboard unavailable
- Elevated resource utilization
- Individual service degradation

Target response: Normal operational priority.

### SEV-4 — Low

Minor issue with little or no customer impact.

Examples:

- Warning-level monitoring event
- Non-critical configuration issue
- Documentation or maintenance task

Target response: Scheduled.

## Incident Documentation

Every simulated incident should record:

- Incident ID
- Date/time
- Severity
- Summary
- Customer impact
- Detection method
- Investigation
- Root cause
- Remediation
- Verification
- Recovery time
- Preventive action

## Incident Philosophy

The goal of incident response is not to assign blame.

The goal is to restore service, understand what happened, and improve the system.
