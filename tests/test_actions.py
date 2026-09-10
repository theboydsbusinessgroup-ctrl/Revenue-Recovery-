import unittest
from revenue_recovery.actions import ContactHistory, ContactPolicy, build_outreach_queue, classify_reply
from revenue_recovery.detector import detect_quote_reactivation
from revenue_recovery.engine import analyze_with_actions
from revenue_recovery.models import QuoteRecord

class ActionLayerTests(unittest.TestCase):
    def quote(self,**kw):
        base=dict(quote_id='Q1',customer_id='C1',quoted_value=1500,created_days_ago=20,last_contact_days_ago=10,status='quoted',contactable=True,opted_out=False,prior_customer=False,engagement_count=2,source_ref='crm:Q1')
        base.update(kw); return QuoteRecord(**base)

    def test_first_followup_is_dry_run(self):
        q=self.quote(); opp=detect_quote_reactivation([q])
        item=build_outreach_queue(opp,[q])[0]
        self.assertFalse(item.suppressed)
        self.assertTrue(item.dry_run)

    def test_frequency_limit_suppresses_fast_repeat(self):
        q=self.quote(); opp=detect_quote_reactivation([q])
        item=build_outreach_queue(opp,[q],[ContactHistory('Q1',attempts=1,last_contact_days_ago=2)])[0]
        self.assertTrue(item.suppressed)
        self.assertEqual(item.suppression_reason,'contact_frequency_limit')

    def test_max_attempts_stops_outreach(self):
        q=self.quote(); opp=detect_quote_reactivation([q])
        item=build_outreach_queue(opp,[q],[ContactHistory('Q1',attempts=3,last_contact_days_ago=20)])[0]
        self.assertEqual(item.suppression_reason,'max_recovery_attempts_reached')

    def test_negative_reply_stops_outreach(self):
        q=self.quote(); opp=detect_quote_reactivation([q])
        item=build_outreach_queue(opp,[q],[ContactHistory('Q1',attempts=1,last_contact_days_ago=20,negative_reply=True)])[0]
        self.assertEqual(item.suppression_reason,'negative_reply')

    def test_reply_classification(self):
        self.assertEqual(classify_reply('Yes, let us move forward'),'positive')
        self.assertEqual(classify_reply('No thanks, we went with someone else'),'negative')
        self.assertEqual(classify_reply('Please unsubscribe'),'opt_out')
        self.assertEqual(classify_reply('Circle back next month'),'defer')

    def test_engine_never_sends_in_action_phase(self):
        report=analyze_with_actions([self.quote()])
        self.assertEqual(report['send_mode'],'dry_run_only')
        self.assertEqual(report['messages_sent'],0)
        self.assertEqual(report['ready_to_send_count'],1)

if __name__=='__main__':unittest.main()
