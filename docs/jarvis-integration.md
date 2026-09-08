# JARVIS Integration Contract

JARVIS is the portfolio visibility/orchestration layer; Revenue Recovery owns operational truth and execution authority.

## Telemetry published to JARVIS

```text
active_clients
pipeline_candidates
ready_recovery_opportunities
contacted_opportunities
qualified_opportunities
won_recoveries
verified_recovered_revenue
recovery_fees
contribution_income
client_conversion_rate
recovery_rate
average_recovered_value
pipeline_value
agent_runs
agent_failures
human_review_queue
suppressed_contacts
opt_out_count
integration_health
data_freshness
last_successful_run
```

Every metric must carry a source and freshness timestamp. Estimated values must be explicitly marked estimated.

## Authority

JARVIS may:
- observe Revenue Recovery telemetry;
- compare performance against portfolio priorities;
- recommend reprioritization;
- surface exceptions;
- request permitted workflow runs through the Revenue Recovery authority boundary once an authenticated integration exists.

JARVIS may not:
- bypass suppression/opt-out controls;
- directly send customer messages;
- alter attribution records;
- move money;
- change credentials;
- override compliance gates;
- claim revenue that Revenue Recovery has not verified.

## Events

Recommended event envelope:

```json
{
  "event_type": "recovery.verified",
  "event_id": "opaque-id",
  "occurred_at": "ISO-8601",
  "source": "revenue-recovery",
  "entity_id": "opaque-id",
  "amount": 0,
  "currency": "USD",
  "status": "verified",
  "metadata": {}
}
```

Do not send passwords, payment-card data, raw credentials, or unnecessary customer PII to JARVIS.

## Portfolio role

JARVIS should use Revenue Recovery's verified contribution income when ranking projects and forecasting portfolio cash flow. It should prioritize the earliest path to validated revenue while preserving safety and domain-specific authority.
