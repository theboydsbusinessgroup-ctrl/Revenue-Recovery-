import unittest
from revenue_recovery.ledger import EvidenceRef, merge_evidence
from revenue_recovery.telemetry import jarvis_snapshot

class TelemetryTests(unittest.TestCase):
    def test_snapshot_excludes_pii_and_preserves_truth(self):
        rows=merge_evidence([EvidenceRef('stripe_invoice','in_1','client@example.com','cus_1',None,125,'USD','open',True,None,['stripe:in_1'])])
        snap=jarvis_snapshot(rows,source_commit='abc',generated_at='2026-09-10T17:55:00Z')
        self.assertEqual(snap['metrics']['ready_recovery_opportunities'],1)
        self.assertEqual(snap['metrics']['recoverable_value_identified'],125)
        self.assertEqual(snap['metrics']['verified_recovered_revenue'],0)
        self.assertFalse(snap['privacy']['customer_pii_included'])
        self.assertNotIn('client@example.com',str(snap))

    def test_suppression_counts_roll_up_without_identity(self):
        rows=merge_evidence([EvidenceRef('stripe_payment_intent','pi_1',None,None,None,100,'USD','requires_payment_method',False,'missing_customer_identity',['stripe:pi_1'])])
        snap=jarvis_snapshot(rows,generated_at='2026-09-10T17:55:00Z')
        self.assertEqual(snap['metrics']['ready_recovery_opportunities'],0)
        self.assertEqual(snap['suppression_counts']['missing_customer_identity'],1)

if __name__=='__main__':unittest.main()
