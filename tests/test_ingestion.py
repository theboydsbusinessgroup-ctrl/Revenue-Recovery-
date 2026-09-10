import unittest
from revenue_recovery.engine import analyze_csv
from revenue_recovery.ingestion import ingest_csv_text

class IngestionTests(unittest.TestCase):
 def test_alias_headers_and_currency_normalize(self):
  text='quote,client,amount,age_days,days_since_contact,stage,can_contact,dnc,existing_customer,touches\nQ1,C1,"$1,500.00",20,10,quoted,yes,no,yes,3\n'
  result=ingest_csv_text(text)
  self.assertEqual(len(result.records),1)
  r=result.records[0]
  self.assertEqual(r.quoted_value,1500.0)
  self.assertTrue(r.prior_customer)

 def test_bad_rows_are_rejected_not_guessed(self):
  text='quote_id,customer_id,quoted_value,created_days_ago,last_contact_days_ago,status\n,C1,abc,10,8,quoted\n'
  result=ingest_csv_text(text)
  self.assertEqual(len(result.records),0)
  self.assertEqual(len(result.rejected),1)
  self.assertIn('missing_quote_id',result.rejected[0].reasons)
  self.assertIn('invalid_quoted_value',result.rejected[0].reasons)

 def test_csv_flows_into_recovery_queue(self):
  text='quote_id,customer_id,quoted_value,created_days_ago,last_contact_days_ago,status,contactable,opted_out\nQ1,C1,1800,21,14,quoted,true,false\nQ2,C2,900,3,2,quoted,true,false\n'
  report=analyze_csv(text)
  self.assertEqual(report['records_analyzed'],2)
  self.assertEqual(report['actionable_opportunities'],1)
  self.assertEqual(report['recoverable_value_identified'],1800)
  self.assertEqual(report['ingestion']['accepted'],2)
  self.assertEqual(report['revenue_claimed'],0)

if __name__=='__main__': unittest.main()
