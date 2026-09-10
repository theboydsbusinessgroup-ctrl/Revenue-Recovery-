# Jarvis telemetry snapshot

`revenue_recovery.telemetry.jarvis_snapshot()` exports a PII-safe aggregate view for Jarvis. It contains canonical opportunity counts, actionable/suppressed counts, identified recoverable value, verified recovered revenue, suppression rollups, blockers, freshness, and recommended actions.

The snapshot intentionally excludes customer names, email addresses, raw messages, quote bodies, credentials, and payment details. Jarvis receives portfolio visibility, not operational customer records.

`recoverable_value_identified` is opportunity value only. `verified_recovered_revenue` remains zero unless Revenue Recovery has authoritative evidence of a completed recovery payment.
