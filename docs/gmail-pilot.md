# Gmail real-data pilot rules

The first Gmail pilot intentionally distinguishes direct customer conversations from lead-platform notifications.

Current source guards:
- Thumbtack and other configured marketplace notification domains are not treated as customer quote records.
- no-reply/do-not-reply senders are not eligible recipients.
- a recent direct outbound contact inside the recovery frequency window suppresses additional recovery action.
- malformed timestamps are rejected rather than guessed.

Pilot result on 2026-09-10: a recent sample of quote-heavy Boyd's Bar threads consisted of Thumbtack lead notifications rather than direct customer quote conversations. Those records were therefore excluded from the recovery queue. A verified direct prior contact had been contacted the same day and was frequency-gated, so no external recovery draft was created.

This is expected behavior: Revenue Recovery should prefer a smaller evidenced queue over inflating opportunity counts with third-party lead alerts.
