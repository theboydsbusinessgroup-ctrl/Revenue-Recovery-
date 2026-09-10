from __future__ import annotations
from .ledger import EvidenceRef
from .models import QuoteRecord, RecoveryOpportunity
from .stripe_source import StripeRecoverySignal


def from_quote_record(q: QuoteRecord, opportunity: RecoveryOpportunity | None = None) -> EvidenceRef:
    return EvidenceRef(
        source_type="csv_quote",
        source_id=q.quote_id,
        customer_id=q.customer_id,
        external_key=q.quote_id,
        amount=(opportunity.expected_recoverable_value if opportunity else q.quoted_value),
        currency="USD",
        status=q.status,
        recoverable=(False if opportunity and opportunity.suppressed else True),
        suppression_reason=(opportunity.suppression_reason if opportunity else None),
        evidence=(opportunity.evidence[:] if opportunity else [q.source_ref] if q.source_ref else []),
    )


def from_stripe_signal(s: StripeRecoverySignal) -> EvidenceRef:
    external_key = None
    for item in s.evidence:
        if item.startswith("metadata:booking_id="):
            external_key = "booking:" + item.split("=", 1)[1]
            break
    return EvidenceRef(
        source_type=f"stripe_{s.source_type}",
        source_id=s.source_id,
        customer_email=s.customer_email,
        customer_id=s.customer_id,
        external_key=external_key,
        amount=s.amount,
        currency=s.currency or "USD",
        status=s.status,
        recoverable=s.recoverable,
        suppression_reason=s.suppression_reason,
        evidence=s.evidence[:],
    )


def from_gmail_contact(*, thread_id: str, customer_email: str | None, external_key: str | None = None, recoverable: bool, suppression_reason: str | None = None, evidence: list[str] | None = None) -> EvidenceRef:
    return EvidenceRef(
        source_type="gmail_thread",
        source_id=thread_id,
        customer_email=customer_email,
        external_key=external_key,
        amount=0.0,
        currency="USD",
        status="contact_evidence",
        recoverable=recoverable,
        suppression_reason=suppression_reason,
        evidence=evidence or [f"gmail:thread:{thread_id}"],
    )
