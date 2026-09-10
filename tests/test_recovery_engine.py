import unittest
from revenue_recovery.engine import analyze
from revenue_recovery.models import QuoteRecord

class RecoveryEngineTests(unittest.TestCase):
    def test_stale_quote_becomes_actionable_opportunity(self):
        report = analyze([QuoteRecord("Q1","C1",1500,20,10,"quoted",True,False,False,2,"crm:Q1")])
        self.assertEqual(report["actionable_opportunities"],1)
        self.assertEqual(report["recoverable_value_identified"],1500)
        self.assertEqual(report["revenue_claimed"],0)

    def test_won_quote_is_not_recovered_again(self):
        report = analyze([QuoteRecord("Q1","C1",1500,20,10,"won")])
        self.assertEqual(report["opportunities_found"],0)

    def test_opt_out_is_suppressed(self):
        report = analyze([QuoteRecord("Q1","C1",1500,20,10,"quoted",True,True)])
        self.assertEqual(report["opportunities_found"],1)
        self.assertEqual(report["actionable_opportunities"],0)
        self.assertTrue(report["queue"][0]["suppressed"])

    def test_recent_quote_is_not_touched(self):
        report = analyze([QuoteRecord("Q1","C1",1500,3,2,"quoted")])
        self.assertEqual(report["opportunities_found"],0)

    def test_expired_quote_is_not_reactivated(self):
        report = analyze([QuoteRecord("Q1","C1",1500,200,150,"quoted")])
        self.assertEqual(report["opportunities_found"],0)

if __name__ == "__main__": unittest.main()
