# Stripe canonicalization truth rule

Stripe source signals are not themselves canonical recovery opportunities.

When multiple PaymentIntents carry the same authoritative booking identifier, each signal is first normalized through `from_stripe_signal`, then passed through `merge_evidence`. The resulting telemetry must count the canonical opportunity, not the number of underlying Stripe objects.

For the currently observed shape—two incomplete PaymentIntents sharing `booking_id=584`, with no customer or contact identity—the expected canonical result is:

- 1 canonical opportunity;
- 0 ready recovery opportunities;
- 1 suppressed opportunity;
- $0 recoverable value identified;
- $0 verified recovered revenue;
- suppression reason `missing_customer_identity`.

This rule prevents duplicate payment objects from inflating opportunity counts or recoverable-value telemetry.
