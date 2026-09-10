from __future__ import annotations
from typing import Protocol
from .actions import OutreachItem

class DraftProvider(Protocol):
    def create_draft(self, recipient: str, item: OutreachItem) -> dict: ...

class CallbackDraftProvider:
    """Provider boundary for external Gmail/CRM draft tooling.

    The callback is injected by the runtime; credentials never live in this repo.
    """
    def __init__(self, create_callback):
        self.create_callback=create_callback

    def create_draft(self, recipient: str, item: OutreachItem) -> dict:
        if item.suppressed:
            return {'created':False,'reason':item.suppression_reason}
        response=self.create_callback({'recipient_email':recipient,'subject':item.subject,'body':item.body,'is_html':False})
        draft_id=str(response.get('draft_id') or response.get('id') or '')
        if not draft_id:
            raise ValueError('Draft provider did not return a draft ID')
        return {'created':True,'draft_id':draft_id}
