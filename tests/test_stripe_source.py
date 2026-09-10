import unittest
from revenue_recovery.stripe_source import from_invoice,from_payment_intent,summarize

class StripeSourceTests(unittest.TestCase):
 def test_open_positive_invoice_is_recoverable(self):
  s=from_invoice({'id':'in_1','status':'open','amount_remaining':25000,'currency':'usd','customer':'cus_1','customer_email':'client@example.com','livemode':True,'created':1})
  self.assertTrue(s.recoverable); self.assertEqual(s.amount,250.0)

 def test_zero_invoice_is_not_recoverable(self):
  s=from_invoice({'id':'in_1','status':'paid','amount_due':0,'currency':'usd','customer':'cus_1','customer_email':'owner@example.com','livemode':True},self_emails={'owner@example.com'})
  self.assertFalse(s.recoverable); self.assertIn(s.suppression_reason,{'zero_value','self_record'})

 def test_unidentified_requires_payment_method_is_suppressed(self):
  s=from_payment_intent({'id':'pi_1','status':'requires_payment_method','amount':10000,'currency':'usd','customer':None,'receipt_email':None,'livemode':True,'last_payment_error':None,'latest_charge':None,'metadata':{'booking_id':'584'}})
  self.assertFalse(s.recoverable); self.assertEqual(s.suppression_reason,'missing_customer_identity')

 def test_identified_failed_payment_can_be_recovery_signal(self):
  s=from_payment_intent({'id':'pi_2','status':'requires_payment_method','amount':9900,'currency':'usd','customer':'cus_2','receipt_email':'client@example.com','livemode':True,'last_payment_error':{'code':'card_declined'},'latest_charge':'ch_1'})
  self.assertTrue(s.recoverable); self.assertIsNone(s.suppression_reason)

 def test_summary_never_claims_revenue(self):
  s=from_invoice({'id':'in_2','status':'open','amount_remaining':5000,'currency':'usd','customer':'cus_2','customer_email':'c@example.com','livemode':True})
  r=summarize([s]); self.assertEqual(r['recoverable_value_identified'],50.0); self.assertEqual(r['revenue_claimed'],0.0)

if __name__=='__main__':unittest.main()
