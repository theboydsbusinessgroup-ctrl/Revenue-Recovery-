# Stripe authoritative recovery source

Stripe is treated as an authoritative source for invoice and payment-state evidence, but not every incomplete Stripe object is a recovery opportunity.

## Actionable invoice states
A live invoice may become a recovery signal only when it is open or uncollectible, has positive remaining value, and has usable customer identity. Zero-value, paid, test-mode, and self records are suppressed.

## Actionable PaymentIntent states
`requires_payment_method`, `requires_action`, and `requires_confirmation` can indicate incomplete collection. Outreach is suppressed when customer/contact identity is missing. A `requires_payment_method` object with no payment error and no charge is treated as an incomplete checkout rather than a confirmed failed payment.

## Current pilot result
The connected Stripe account currently has no open or uncollectible invoices. It has two live-mode $100 PaymentIntents in `requires_payment_method`, both with booking metadata but no customer, receipt email, payment method, charge, or payment error. They are preserved as authoritative signals but suppressed from recovery outreach.

Recoverable value is never reported as recovered revenue until a downstream successful payment event verifies it.
# Currency scope

Stripe ingestion currently accepts USD only. Missing or other currencies raise
`ValueError` before an opportunity is created, including zero-decimal currencies
such as JPY and three-decimal currencies such as KWD. Add verified Stripe
minor-unit conversion rules and currency-specific ledgers before expanding this
scope. Negative, fractional-minor-unit and non-finite amounts are rejected.

Raw signal summaries expose `amounts_by_currency`; their combined amount is
`null` and currency is `MIXED` when multiple currencies are present. Canonical
ledger and Jarvis telemetry also keep mixed-currency combined amounts `null`.
