from __future__ import annotations
from .models import QuoteRecord, RecoveryOpportunity


def score_opportunity(opportunity: RecoveryOpportunity, quote: QuoteRecord) -> float:
    value = min(max(quote.quoted_value, 0) / 5000.0, 1.0)
    recency = max(0.0, 1.0 - max(quote.last_contact_days_ago - 7, 0) / 113.0)
    engagement = min(quote.engagement_count / 5.0, 1.0)
    prior = 1.0 if quote.prior_customer else 0.0
    contact = 1.0 if quote.contactable and not quote.opted_out else 0.0
    score = 100 * (0.30 * value + 0.25 * recency + 0.15 * engagement + 0.15 * prior + 0.15 * contact)
    if opportunity.suppressed:
        score = 0.0
    return round(score, 1)


def rank(opportunities: list[RecoveryOpportunity], quotes: list[QuoteRecord]) -> list[RecoveryOpportunity]:
    by_id = {q.quote_id: q for q in quotes}
    for o in opportunities:
        o.score = score_opportunity(o, by_id[o.quote_id])
    return sorted(opportunities, key=lambda o: (o.suppressed, -o.score, -o.expected_recoverable_value))
