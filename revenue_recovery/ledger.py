from __future__ import annotations
from dataclasses import dataclass, field, asdict
from hashlib import sha256
from typing import Any, Iterable

@dataclass
class EvidenceRef:
    source_type: str
    source_id: str
    customer_email: str | None = None
    customer_id: str | None = None
    external_key: str | None = None
    amount: float = 0.0
    currency: str = "USD"
    status: str = "unknown"
    recoverable: bool = False
    suppression_reason: str | None = None
    evidence: list[str] = field(default_factory=list)

@dataclass
class CanonicalOpportunity:
    opportunity_id: str
    identity_key: str
    customer_email: str | None
    customer_ids: list[str]
    source_refs: list[EvidenceRef]
    recoverable_value_identified: float
    currency: str
    recoverable: bool
    suppression_reasons: list[str]
    evidence: list[str]

    def as_dict(self) -> dict[str, Any]:
        out = asdict(self)
        return out


def _norm_email(value: str | None) -> str | None:
    return (value or "").strip().lower() or None


def _identity_key(ref: EvidenceRef) -> str:
    email = _norm_email(ref.customer_email)
    if email:
        return f"email:{email}"
    if ref.external_key:
        return f"external:{ref.external_key}"
    if ref.customer_id:
        return f"customer:{ref.customer_id}"
    return f"source:{ref.source_type}:{ref.source_id}"


def _opportunity_id(identity_key: str) -> str:
    return sha256(identity_key.encode()).hexdigest()[:20]


def merge_evidence(refs: Iterable[EvidenceRef]) -> list[CanonicalOpportunity]:
    grouped: dict[str, list[EvidenceRef]] = {}
    for ref in refs:
        grouped.setdefault(_identity_key(ref), []).append(ref)

    opportunities: list[CanonicalOpportunity] = []
    for identity_key, items in grouped.items():
        currencies = {str(i.currency or "USD").upper() for i in items}
        currency = next(iter(currencies)) if len(currencies) == 1 else "MIXED"
        amounts = [max(0.0, float(i.amount or 0)) for i in items if i.recoverable]
        # Same opportunity can surface in multiple systems. Use max, not sum, to avoid double counting.
        value = round(max(amounts) if amounts else 0.0, 2)
        email = next((_norm_email(i.customer_email) for i in items if _norm_email(i.customer_email)), None)
        customer_ids = sorted({i.customer_id for i in items if i.customer_id})
        suppressions = sorted({i.suppression_reason for i in items if i.suppression_reason})
        evidence = sorted({e for i in items for e in i.evidence})
        recoverable = any(i.recoverable for i in items) and not all(i.suppression_reason for i in items)
        opportunities.append(CanonicalOpportunity(
            opportunity_id=_opportunity_id(identity_key),
            identity_key=identity_key,
            customer_email=email,
            customer_ids=customer_ids,
            source_refs=items,
            recoverable_value_identified=value,
            currency=currency,
            recoverable=recoverable,
            suppression_reasons=suppressions,
            evidence=evidence,
        ))
    return sorted(opportunities, key=lambda o: (not o.recoverable, -o.recoverable_value_identified, o.opportunity_id))


def summarize(opportunities: list[CanonicalOpportunity]) -> dict[str, Any]:
    actionable = [o for o in opportunities if o.recoverable]
    currencies = {o.currency for o in actionable if o.currency != "MIXED"}
    total = round(sum(o.recoverable_value_identified for o in actionable), 2) if len(currencies) <= 1 else None
    return {
        "canonical_opportunities": len(opportunities),
        "actionable_opportunities": len(actionable),
        "recoverable_value_identified": total,
        "currency": next(iter(currencies)) if len(currencies) == 1 else ("MIXED" if currencies else "USD"),
        "revenue_claimed": 0.0,
        "queue": [o.as_dict() for o in opportunities],
        "truth_rule": "canonical_recoverable_value_is_not_recovered_revenue",
    }
