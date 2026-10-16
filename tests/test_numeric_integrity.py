import json
import unittest

from revenue_recovery.ingestion import ingest_csv_text
from revenue_recovery.ledger import EvidenceRef, merge_evidence, summarize
from revenue_recovery.telemetry import jarvis_snapshot


class NumericIntegrityTests(unittest.TestCase):
    def test_nonfinite_money_is_rejected(self):
        for amount in ('NaN', 'inf', '-inf'):
            with self.subTest(amount=amount):
                result = ingest_csv_text('quote_id,customer_id,quoted_value,status\n'
                                         f'Q1,C1,{amount},quoted\n')
                self.assertEqual(result.records, [])
                self.assertIn('invalid_quoted_value', result.rejected[0].reasons)
                json.dumps(result.summary(), allow_nan=False)

    def test_nonfinite_fractional_and_negative_ages_are_rejected(self):
        for age in ('inf', 'NaN', '1.5', '-0.5'):
            with self.subTest(age=age):
                result = ingest_csv_text('quote_id,customer_id,quoted_value,created_days_ago,status\n'
                                         f'Q1,C1,100,{age},quoted\n')
                self.assertEqual(result.records, [])
                self.assertIn('invalid_created_days_ago', result.rejected[0].reasons)

    def test_mixed_currency_opportunity_has_no_total_in_any_report(self):
        rows = merge_evidence([
            EvidenceRef('invoice', 'usd', customer_email='c@example.com',
                        amount=100, currency='USD', recoverable=True),
            EvidenceRef('invoice', 'eur', customer_email='c@example.com',
                        amount=200, currency='EUR', recoverable=True),
        ])
        reports = [summarize(rows), jarvis_snapshot(rows)['metrics']]
        for report in reports:
            self.assertIsNone(report['recoverable_value_identified'])
            self.assertEqual(report['currency'], 'MIXED')

    def test_mixed_opportunity_cannot_be_hidden_by_usd_opportunity(self):
        rows = merge_evidence([
            EvidenceRef('invoice', 'usd1', customer_email='c@example.com',
                        amount=100, currency='USD', recoverable=True),
            EvidenceRef('invoice', 'eur', customer_email='c@example.com',
                        amount=200, currency='EUR', recoverable=True),
            EvidenceRef('invoice', 'usd2', customer_email='other@example.com',
                        amount=50, currency='USD', recoverable=True),
        ])
        for report in [summarize(rows), jarvis_snapshot(rows)['metrics']]:
            self.assertIsNone(report['recoverable_value_identified'])
            self.assertEqual(report['currency'], 'MIXED')
