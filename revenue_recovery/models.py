from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Any

@dataclass
class QuoteRecord:
    quote_id: str
    customer_id: str
    quoted_value: float
    created_days_ago: int
    last_contact_days_ago: int
    status: str
    contactable: bool = True
    opted_out: bool = False
    prior_customer: bool = False
    engagement_count: int = 0
    source_ref: str = ""

@dataclass
class RecoveryOpportunity:
    opportunity_id: str
    quote_id: str
    customer_id: str
    reason: str
    expected_recoverable_value: float
    score: float
    recommended_action: str
    evidence: list[str] = field(default_factory=list)
    suppressed: bool = False
    suppression_reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
