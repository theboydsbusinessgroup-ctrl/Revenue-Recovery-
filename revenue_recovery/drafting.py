from __future__ import annotations
from .actions import OutreachItem
from .persistence import RecoveryStore
from .providers import DraftProvider


def create_recovery_draft(item: OutreachItem, recipient: str, provider: DraftProvider, store: RecoveryStore) -> dict:
    if item.suppressed:
        return {'created':False,'reason':item.suppression_reason}
    existing=store.draft_for(item.opportunity_id)
    if existing and existing.get('provider_draft_id'):
        return {'created':False,'reason':'duplicate_draft','draft_id':existing['provider_draft_id']}
    result=provider.create_draft(recipient,item)
    if result.get('created'):
        store.record_draft(item.opportunity_id,item.quote_id,recipient,item.subject,result['draft_id'])
    return result
