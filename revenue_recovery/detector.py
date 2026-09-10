from __future__ import annotations
import hashlib
from .models import QuoteRecord, RecoveryOpportunity


def _id(quote_id: str, reason: str) -> str:
    return hashlib.sha256(f"{quote_id}|{reason}".encode()).hexdigest()[:18]


def detect_quote_reactivation(records: list[QuoteRecord], *, stale_after_days: int = 7, expire_after_days: int = 120) -> list[RecoveryOpportunity]:
    opportunities = []
    for q in records:
        if q.status.lower() in {"won", "paid", "booked", "closed_won"}:
            continue
        if q.created_days_ago > expire_after_days:
            continue
        stale = q.last_contact_days_ago >= stale_after_days
        open_status = q.status.lower() in {"quoted", "estimate_sent", "proposal_sent", "open", "stale"}
        if not (stale and open_status):
            continue
        evidence = [f"quote:{q.quote_id}", f"quoted_value:{q.quoted_value:.2f}", f"last_contact_days_ago:{q.last_contact_days_ago}"]
        if q.source_ref:
            evidence.append(q.source_ref)
        opportunity = RecoveryOpportunity(
            opportunity_id=_id(q.quote_id, "stale_quote"), quote_id=q.quote_id, customer_id=q.customer_id,
            reason="stale_quote", expected_recoverable_value=round(max(0.0, q.quoted_value), 2), score=0.0,
            recommended_action="Send a concise quote follow-up with a clear next step and preserved original pricing.", evidence=evidence,
        )
        if q.opted_out:
            opportunity.suppressed = True; opportunity.suppression_reason = "customer_opted_out"
        elif not q.contactable:
            opportunity.suppressed = True; opportunity.suppression_reason = "no_permitted_contact_channel"
        opportunities.append(opportunity)
    return opportunities
