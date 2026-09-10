# Canonical Recovery Opportunity Ledger

The ledger merges recovery evidence from Gmail, CSV/manual exports, and Stripe into one canonical opportunity queue.

## Identity and deduplication
Evidence is grouped by the strongest available identity in this order: normalized customer email, explicit external/business key such as booking ID, customer ID, then source object ID as a safe fallback.

When the same commercial opportunity appears in multiple systems, recoverable value is **not summed**. The ledger uses the maximum evidenced recoverable amount for that canonical opportunity to avoid double counting a quote in CSV and the same amount in Stripe.

## Source lineage
Every canonical opportunity retains all contributing source references and evidence strings. Jarvis can therefore show one opportunity while still exposing where the conclusion came from.

## Suppression
Unidentified or suppressed source objects remain visible but are not automatically actionable. The ledger does not use source count as proof of customer identity or permission to contact.

## Revenue truth
`recoverable_value_identified` remains opportunity value only. `revenue_claimed` remains zero until an authoritative successful payment or booking event proves recovery.
