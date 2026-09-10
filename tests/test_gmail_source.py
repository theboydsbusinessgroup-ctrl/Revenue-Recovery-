import unittest
from datetime import datetime, timezone
from revenue_recovery.gmail_source import MailSignal, assess_signal, assess_thread

NOW=datetime(2026,9,10,17,43,tzinfo=timezone.utc)

class GmailSourceTests(unittest.TestCase):
 def test_thumbtack_notification_is_not_customer_quote(self):
  s=MailSignal('t1','Thumbtack <do-not-reply@pro.thumbtack.com>','business@example.com','Customer needs Bartending','2026-09-10T13:55:09Z')
  a=assess_signal(s,now=NOW)
  self.assertFalse(a.recoverable_source)
  self.assertEqual(a.suppression_reason,'third_party_lead_notification')

 def test_recent_direct_outbound_contact_is_frequency_gated(self):
  s=MailSignal('t2','business@example.com','client@example.com','Quick resource','2026-09-10T12:22:06Z','outbound')
  a=assess_signal(s,now=NOW)
  self.assertTrue(a.direct_customer_contact)
  self.assertFalse(a.recoverable_source)
  self.assertEqual(a.suppression_reason,'recent_contact_frequency_gate')

 def test_old_direct_contact_can_be_recovery_source(self):
  s=MailSignal('t3','client@example.com','business@example.com','Event details','2026-08-20T12:00:00Z','inbound')
  a=assess_signal(s,now=NOW)
  self.assertTrue(a.recoverable_source)

 def test_thread_with_third_party_lead_alert_is_excluded(self):
  msgs=[MailSignal('t4','Thumbtack <do-not-reply@pro.thumbtack.com>','business@example.com','Lead','2026-09-01T12:00:00Z')]
  a=assess_thread(msgs,now=NOW)
  self.assertEqual(a.suppression_reason,'third_party_lead_notification')

if __name__=='__main__':unittest.main()
