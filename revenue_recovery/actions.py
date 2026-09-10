from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterable
from .models import QuoteRecord, RecoveryOpportunity

@dataclass(frozen=True)
class ContactPolicy:
    min_days_between_contacts:int=7
    max_recovery_attempts:int=3
    stop_on_opt_out:bool=True
    stop_on_negative_reply:bool=True

@dataclass
class ContactHistory:
    quote_id:str
    attempts:int=0
    last_contact_days_ago:int=999
    negative_reply:bool=False

@dataclass
class OutreachItem:
    opportunity_id:str
    quote_id:str
    customer_id:str
    subject:str
    body:str
    dry_run:bool=True
    suppressed:bool=False
    suppression_reason:str|None=None

    def as_dict(self)->dict:
        return asdict(self)

TEMPLATES={
    "first_follow_up": {
        "subject":"Quick follow-up on your quote",
        "body":"Hi — I wanted to follow up on the quote we sent. If you'd like to move forward, reply here and we'll help with the next step. If your plans changed, no problem — just let us know."
    },
    "second_follow_up": {
        "subject":"Checking in on your quote",
        "body":"Hi — just checking in once more on the quote we sent. If the timing is still right, reply here and we'll pick up where we left off. If not, we'll close the loop for now."
    },
    "final_follow_up": {
        "subject":"Closing the loop on your quote",
        "body":"Hi — this is our final follow-up on the quote we sent. If you'd still like to continue, reply anytime and we'll help with next steps. Otherwise, we'll close this out for now."
    }
}


def classify_reply(text:str)->str:
    t=(text or "").strip().lower()
    if not t:return "unknown"
    if any(x in t for x in ["unsubscribe","stop contacting","do not contact","don't contact"]):return "opt_out"
    if any(x in t for x in ["not interested","no thanks","no thank you","we passed","went with someone else"]):return "negative"
    if any(x in t for x in ["yes","interested","move forward","book","let's do it","lets do it","call me","send the link"]):return "positive"
    if any(x in t for x in ["later","next month","not yet","follow up later","circle back"]):return "defer"
    return "unknown"


def build_outreach_queue(opportunities:list[RecoveryOpportunity], quotes:list[QuoteRecord], histories:Iterable[ContactHistory]=(), policy:ContactPolicy|None=None)->list[OutreachItem]:
    policy=policy or ContactPolicy()
    quote_by_id={q.quote_id:q for q in quotes}
    history_by_id={h.quote_id:h for h in histories}
    queue=[]
    for o in opportunities:
        q=quote_by_id[o.quote_id]
        h=history_by_id.get(o.quote_id,ContactHistory(o.quote_id))
        suppressed=o.suppressed
        reason=o.suppression_reason
        if policy.stop_on_opt_out and q.opted_out:
            suppressed=True; reason="customer_opted_out"
        elif policy.stop_on_negative_reply and h.negative_reply:
            suppressed=True; reason="negative_reply"
        elif h.attempts>=policy.max_recovery_attempts:
            suppressed=True; reason="max_recovery_attempts_reached"
        elif h.attempts>0 and h.last_contact_days_ago<policy.min_days_between_contacts:
            suppressed=True; reason="contact_frequency_limit"
        template_key=("first_follow_up" if h.attempts==0 else "second_follow_up" if h.attempts==1 else "final_follow_up")
        tpl=TEMPLATES[template_key]
        queue.append(OutreachItem(o.opportunity_id,o.quote_id,o.customer_id,tpl["subject"],tpl["body"],True,suppressed,reason))
    return queue
