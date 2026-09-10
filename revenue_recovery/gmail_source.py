from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parseaddr

THIRD_PARTY_LEAD_DOMAINS={
    'pro.thumbtack.com','thumbtack.com','bark.com','barkmail.com','theknot.com','weddingwire.com'
}
NO_REPLY_LOCAL_PARTS={'no-reply','noreply','do-not-reply','donotreply'}

@dataclass
class MailSignal:
    thread_id:str
    sender:str
    recipient:str
    subject:str
    timestamp:str
    direction:str='inbound'

@dataclass
class SourceAssessment:
    direct_customer_contact:bool
    recoverable_source:bool
    suppression_reason:str|None
    sender_email:str
    age_days:int|None


def _email(value:str)->str:
    return parseaddr(value or '')[1].strip().lower()


def assess_signal(signal:MailSignal, *, now:datetime|None=None, min_recovery_age_days:int=7)->SourceAssessment:
    sender=_email(signal.sender)
    local, _, domain=sender.partition('@')
    if domain in THIRD_PARTY_LEAD_DOMAINS:
        return SourceAssessment(False,False,'third_party_lead_notification',sender,None)
    if local in NO_REPLY_LOCAL_PARTS or local.endswith('noreply'):
        return SourceAssessment(False,False,'no_reply_sender',sender,None)
    age=None
    if signal.timestamp:
        try:
            dt=datetime.fromisoformat(signal.timestamp.replace('Z','+00:00'))
            now=now or datetime.now(timezone.utc)
            age=max(0,(now-dt.astimezone(timezone.utc)).days)
        except ValueError:
            return SourceAssessment(True,False,'invalid_message_timestamp',sender,None)
    if signal.direction=='outbound' and age is not None and age<min_recovery_age_days:
        return SourceAssessment(True,False,'recent_contact_frequency_gate',sender,age)
    return SourceAssessment(True,True,None,sender,age)


def assess_thread(messages:list[MailSignal], *, now:datetime|None=None, min_recovery_age_days:int=7)->SourceAssessment:
    if not messages:
        return SourceAssessment(False,False,'empty_thread','',None)
    assessments=[assess_signal(m,now=now,min_recovery_age_days=min_recovery_age_days) for m in messages]
    if any(a.suppression_reason=='third_party_lead_notification' for a in assessments):
        return SourceAssessment(False,False,'third_party_lead_notification',assessments[0].sender_email,None)
    outbound=[(m,a) for m,a in zip(messages,assessments) if m.direction=='outbound']
    if outbound:
        latest=max(outbound,key=lambda x:x[0].timestamp or '')[1]
        if latest.suppression_reason=='recent_contact_frequency_gate':
            return latest
    valid=[a for a in assessments if a.recoverable_source]
    return valid[-1] if valid else assessments[-1]
