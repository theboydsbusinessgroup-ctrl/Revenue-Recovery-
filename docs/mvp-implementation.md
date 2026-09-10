# Executable MVP: stale quote reactivation

The first runtime intentionally solves one narrow problem: identify open quotes/estimates that have gone stale but are still within a configurable reactivation window.

The detector does not call identified value "revenue." It reports `recoverable_value_identified` separately and keeps `revenue_claimed` at zero until a downstream authoritative payment/booking event can prove recovery.

## Current gates
- won/paid/booked records are ignored
- old/expired records are ignored
- customer opt-outs are suppressed
- records with no permitted contact channel are suppressed
- recommended action preserves existing pricing; no fabricated discount is introduced
- source/evidence references travel with each opportunity

## Next vertical step
Add a CSV/manual-export normalizer for a zero-cost pilot, then produce a recovery queue from real authorized business data without sending outreach automatically until messaging and compliance rules are configured.
