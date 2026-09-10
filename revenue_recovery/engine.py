from __future__ import annotations
from .detector import detect_quote_reactivation
from .models import QuoteRecord
from .scoring import rank
from .ingestion import ingest_csv_text


def analyze(records: list[QuoteRecord]) -> dict:
    opportunities = rank(detect_quote_reactivation(records), records)
    actionable = [o for o in opportunities if not o.suppressed]
    return {
        "records_analyzed": len(records),
        "opportunities_found": len(opportunities),
        "actionable_opportunities": len(actionable),
        "recoverable_value_identified": round(sum(o.expected_recoverable_value for o in actionable), 2),
        "queue": [o.as_dict() for o in opportunities],
        "revenue_claimed": 0.0,
        "truth_rule": "identified_value_is_not_recovered_revenue",
    }


def analyze_csv(text: str) -> dict:
    ingestion = ingest_csv_text(text)
    report = analyze(ingestion.records)
    report["ingestion"] = ingestion.summary()
    return report
