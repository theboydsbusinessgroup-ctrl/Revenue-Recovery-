# Jarvis telemetry snapshot

`revenue_recovery.telemetry.jarvis_snapshot()` exports a PII-safe aggregate view for Jarvis. It contains canonical opportunity counts, actionable/suppressed counts, identified recoverable value, verified recovered revenue, suppression rollups, blockers, freshness, and recommended actions.

The snapshot intentionally excludes customer names, email addresses, raw messages, quote bodies, credentials, and payment details. Jarvis receives portfolio visibility, not operational customer records.

## Source signals versus canonical opportunities

`source_signal_references` reports how many underlying source records support the canonical ledger. `canonical_opportunities` reports the deduplicated opportunities after identity resolution. `duplicate_source_signals_collapsed` makes the difference explicit.

For example, two Stripe PaymentIntents carrying the same `booking_id` are two source signals but one canonical opportunity. They must never be shown as two recovery opportunities or have their values summed merely because two source records exist.

`recoverable_value_identified` is opportunity value only. `verified_recovered_revenue` remains zero unless Revenue Recovery has authoritative evidence of a completed recovery payment.
