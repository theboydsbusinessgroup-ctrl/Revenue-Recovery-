from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class StripeRecoverySignal:
    source_type:str
    source_id:str
    amount:float
    currency:str
    status:str
    customer_id:str|None
    customer_email:str|None
    created:int|None
    recoverable:bool
    suppression_reason:str|None
    evidence:list[str]

    def as_dict(self)->dict[str,Any]:
        return asdict(self)


def _money(cents:int|float|None)->float:
    return round(max(0.0,float(cents or 0))/100.0,2)


def from_invoice(invoice:dict[str,Any], *, self_emails:set[str]|None=None)->StripeRecoverySignal:
    self_emails={e.lower() for e in (self_emails or set())}
    email=(invoice.get('customer_email') or '').strip().lower() or None
    amount=_money(invoice.get('amount_remaining') if invoice.get('amount_remaining') is not None else invoice.get('amount_due'))
    status=str(invoice.get('status') or '')
    reason=None
    recoverable=status in {'open','uncollectible'} and amount>0
    if amount<=0:
        recoverable=False; reason='zero_value'
    elif email and email in self_emails:
        recoverable=False; reason='self_record'
    elif invoice.get('livemode') is False:
        recoverable=False; reason='test_mode'
    elif status not in {'open','uncollectible'}:
        recoverable=False; reason='invoice_not_unpaid'
    elif not email and not invoice.get('customer'):
        recoverable=False; reason='missing_customer_identity'
    evidence=[f"stripe:invoice:{invoice.get('id','')}",f"status:{status}",f"amount_remaining:{amount:.2f}"]
    return StripeRecoverySignal('invoice',str(invoice.get('id') or ''),amount,str(invoice.get('currency') or '').upper(),status,invoice.get('customer'),email,invoice.get('created'),recoverable,reason,evidence)


def from_payment_intent(pi:dict[str,Any], *, self_emails:set[str]|None=None)->StripeRecoverySignal:
    self_emails={e.lower() for e in (self_emails or set())}
    email=(pi.get('receipt_email') or '').strip().lower() or None
    amount=_money(pi.get('amount'))
    status=str(pi.get('status') or '')
    recoverable=status in {'requires_payment_method','requires_action','requires_confirmation'} and amount>0
    reason=None
    if amount<=0:
        recoverable=False; reason='zero_value'
    elif pi.get('livemode') is False:
        recoverable=False; reason='test_mode'
    elif email and email in self_emails:
        recoverable=False; reason='self_record'
    elif status not in {'requires_payment_method','requires_action','requires_confirmation'}:
        recoverable=False; reason='payment_state_not_recoverable'
    elif not email and not pi.get('customer'):
        recoverable=False; reason='missing_customer_identity'
    elif not email:
        recoverable=False; reason='missing_contact_email'
    if pi.get('last_payment_error') is None and pi.get('latest_charge') is None and status=='requires_payment_method':
        if reason is None:
            reason='incomplete_checkout_no_failed_charge'
            recoverable=False
    evidence=[f"stripe:payment_intent:{pi.get('id','')}",f"status:{status}",f"amount:{amount:.2f}"]
    md=pi.get('metadata') or {}
    for k in sorted(md):
        evidence.append(f"metadata:{k}={md[k]}")
    return StripeRecoverySignal('payment_intent',str(pi.get('id') or ''),amount,str(pi.get('currency') or '').upper(),status,pi.get('customer'),email,pi.get('created'),recoverable,reason,evidence)


def summarize(signals:list[StripeRecoverySignal])->dict[str,Any]:
    actionable=[s for s in signals if s.recoverable]
    return {
        'signals_found':len(signals),
        'actionable_signals':len(actionable),
        'recoverable_value_identified':round(sum(s.amount for s in actionable),2),
        'revenue_claimed':0.0,
        'signals':[s.as_dict() for s in signals],
        'truth_rule':'stripe_recoverable_value_is_not_recovered_revenue_until_payment_succeeds',
    }
