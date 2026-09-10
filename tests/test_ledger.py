import tempfile, unittest
from pathlib import Path
from revenue_recovery.ledger import EvidenceRef, merge_evidence, summarize
from revenue_recovery.persistence import RecoveryStore

class LedgerTests(unittest.TestCase):
    def test_same_email_from_gmail_and_stripe_merges_once(self):
        refs=[
            EvidenceRef('gmail_thread','t1','client@example.com',None,None,0,'USD','contact_evidence',True,None,['gmail:t1']),
            EvidenceRef('stripe_invoice','in_1','client@example.com','cus_1',None,250,'USD','open',True,None,['stripe:in_1']),
        ]
        rows=merge_evidence(refs)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0].recoverable_value_identified,250)
        self.assertEqual(len(rows[0].source_refs),2)

    def test_duplicate_values_are_not_summed(self):
        refs=[
            EvidenceRef('csv_quote','Q1',None,'C1','booking:584',100,'USD','quoted',True,None,['csv:Q1']),
            EvidenceRef('stripe_payment_intent','pi_1',None,None,'booking:584',100,'USD','requires_payment_method',True,None,['stripe:pi_1']),
        ]
        rows=merge_evidence(refs)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0].recoverable_value_identified,100)

    def test_unidentified_sources_stay_separate(self):
        refs=[EvidenceRef('stripe_payment_intent','pi_1',None,None,None,100,'USD','requires_payment_method',False,'missing_customer_identity',['stripe:pi_1']), EvidenceRef('stripe_payment_intent','pi_2',None,None,None,100,'USD','requires_payment_method',False,'missing_customer_identity',['stripe:pi_2'])]
        self.assertEqual(len(merge_evidence(refs)),2)

    def test_summary_never_claims_revenue(self):
        rows=merge_evidence([EvidenceRef('stripe_invoice','in_1','c@example.com','cus_1',None,50,'USD','open',True,None,['x'])])
        report=summarize(rows)
        self.assertEqual(report['recoverable_value_identified'],50)
        self.assertEqual(report['revenue_claimed'],0)

    def test_canonical_opportunity_persists(self):
        td=tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        store=RecoveryStore(Path(td.name)/'state.db')
        row=merge_evidence([EvidenceRef('stripe_invoice','in_1','c@example.com','cus_1',None,50,'USD','open',True,None,['x'])])[0]
        store.save_canonical_opportunity(row)
        loaded=store.load_canonical_opportunities()
        self.assertEqual(len(loaded),1)
        self.assertEqual(loaded[0]['opportunity_id'],row.opportunity_id)

if __name__=='__main__':unittest.main()
