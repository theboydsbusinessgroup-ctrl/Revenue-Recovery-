from __future__ import annotations
from .detector import detect_quote_reactivation
from .models import QuoteRecord
from .scoring import rank
from .ingestion import ingest_csv_text
from .actions import ContactHistory, ContactPolicy, build_outreach_queue


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


def analyze_with_actions(records:list[QuoteRecord], histories:list[ContactHistory]|None=None, policy:ContactPolicy|None=None)->dict:
    opportunities=rank(detect_quote_reactivation(records),records)
    outreach=build_outreach_queue(opportunities,records,histories or [],policy)
    actionable=[x for x in outreach if not x.suppressed]
    return {
        "analysis": analyze(records),
        "outreach_queue": [x.as_dict() for x in outreach],
        "ready_to_send_count": len(actionable),
        "send_mode": "dry_run_only",
        "messages_sent": 0,
    }


def analyze_csv(text: str) -> dict:
    ingestion = ingest_csv_text(text)
    report = analyze(ingestion.records)
    report["ingestion"] = ingestion.summary()
    return report
