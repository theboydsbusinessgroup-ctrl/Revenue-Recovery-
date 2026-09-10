from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from .ledger import CanonicalOpportunity


def jarvis_snapshot(opportunities: list[CanonicalOpportunity], *, source_commit: str | None = None, generated_at: str | None = None, blockers: list[str] | None = None) -> dict[str, Any]:
    generated_at = generated_at or datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    actionable = [o for o in opportunities if o.recoverable]
    suppressed = [o for o in opportunities if not o.recoverable]
    currencies = {o.currency for o in actionable if o.currency and o.currency != 'MIXED'}
    value = round(sum(o.recoverable_value_identified for o in actionable), 2) if len(currencies) <= 1 else None
    source_signal_references = sum(len(o.source_refs) for o in opportunities)
    duplicate_source_signals_collapsed = max(0, source_signal_references - len(opportunities))
    reasons: dict[str, int] = {}
    for o in suppressed:
        for reason in o.suppression_reasons or ['not_actionable']:
            reasons[reason] = reasons.get(reason, 0) + 1
    return {
        'schema_version': '1.1',
        'source': 'revenue-recovery',
        'generated_at': generated_at,
        'source_commit': source_commit,
        'metrics': {
            'source_signal_references': source_signal_references,
            'duplicate_source_signals_collapsed': duplicate_source_signals_collapsed,
            'canonical_opportunities': len(opportunities),
            'ready_recovery_opportunities': len(actionable),
            'suppressed_opportunities': len(suppressed),
            'recoverable_value_identified': value,
            'currency': next(iter(currencies)) if len(currencies) == 1 else ('MIXED' if currencies else 'USD'),
            'verified_recovered_revenue': 0.0,
            'revenue_truth': 'verified_only',
        },
        'suppression_counts': reasons,
        'blockers': blockers or [],
        'recommended_actions': _recommended_actions(actionable, suppressed, blockers or []),
        'privacy': {
            'customer_pii_included': False,
            'raw_customer_records_included': False,
        },
        'truth_rules': {
            'source_signals_are_not_canonical_opportunities': True,
            'canonical_recoverable_value_is_not_recovered_revenue': True,
        },
    }


def _recommended_actions(actionable: list[CanonicalOpportunity], suppressed: list[CanonicalOpportunity], blockers: list[str]) -> list[str]:
    actions: list[str] = []
    if actionable:
        actions.append('Review eligible recovery opportunities and prepare policy-compliant drafts.')
    if suppressed:
        actions.append('Resolve identity/contact or source-quality suppression reasons where evidence permits.')
    if blockers:
        actions.append('Resolve integration blockers without bypassing recovery policy gates.')
    if not actions:
        actions.append('Continue authorized source ingestion and wait for evidenced recovery opportunities.')
    return actions
