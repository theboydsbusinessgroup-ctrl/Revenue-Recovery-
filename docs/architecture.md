# Revenue Recovery Architecture

## System layers

1. **Connectors** — authorized CRM, spreadsheet, booking, quote, invoice, and messaging integrations.
2. **Ingestion** — import only fields required for recovery decisions; attach source and freshness metadata.
3. **Normalization** — convert source records into a common Lead, Customer, Opportunity, Quote, Appointment, and RecoveryEvent model.
4. **Leakage Detector** — deterministic rules identify stale, abandoned, lapsed, cancelled, or missed-follow-up opportunities.
5. **Scoring Engine** — estimate recoverability using expected value, recency, customer fit, prior engagement, contactability, and compliance status.
6. **Recovery Orchestrator** — selects the next permitted action and enforces frequency/suppression rules.
7. **Conversation/Qualification Layer** — classify replies, answer only approved questions, and hand off sales-ready opportunities.
8. **Attribution Engine** — link recovery activity to subsequent bookings/revenue using explicit evidence and configurable attribution windows.
9. **Reconciliation** — compare attributed recovery against the customer's source-of-truth revenue records.
10. **Telemetry Adapter** — publish aggregate health, pipeline, revenue, margin, and automation metrics to JARVIS.

## State machine

`NEW → INGESTED → CANDIDATE → SCORED → READY → CONTACTED → ENGAGED → QUALIFIED → HANDED_OFF → WON → VERIFIED → RECONCILED`

Alternate states: `SUPPRESSED`, `OPTED_OUT`, `INVALID`, `EXPIRED`, `LOST`, `HUMAN_REVIEW`.

## Scoring model

Initial score is 0–100:

- Expected recoverable value: 25%
- Recency/urgency: 15%
- Historical engagement: 15%
- Customer fit/repeat propensity: 15%
- Contactability/data quality: 10%
- Offer/workflow fit: 10%
- Compliance confidence: 10%

Minimum score for automated recovery should be configurable per vertical. Compliance failure always overrides score.

## Recovery economics

For each opportunity track:

`expected_value → recovery_cost → expected_contribution → realized_revenue → attributable_revenue → recovery_fee → net_revenue`

Revenue is not profit. Contribution calculations must include messaging, AI/API, infrastructure, payment, fulfillment, and other known variable costs.

## Human gates

Human review is required for legal ambiguity, sensitive customer situations, unusual requests, disputed attribution, financial disputes, policy exceptions, and any action outside configured authority.

## MVP vertical

First test harness: quote/lead reactivation for high-ticket home-service businesses. The architecture remains vertical-neutral so additional niches can be added through configuration rather than forks.
