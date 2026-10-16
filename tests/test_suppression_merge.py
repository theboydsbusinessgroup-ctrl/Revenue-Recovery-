import unittest

from revenue_recovery.ledger import EvidenceRef, merge_evidence, summarize


class SuppressionMergeTests(unittest.TestCase):
    def test_other_sources_cannot_override_contact_suppression(self):
        for reason in ('customer_opted_out', 'negative_reply', 'recent_contact_frequency_gate'):
            with self.subTest(reason=reason):
                rows = merge_evidence([
                    EvidenceRef('gmail', 'thread', customer_email='c@example.com',
                                recoverable=False, suppression_reason=reason),
                    EvidenceRef('invoice', 'invoice', customer_email='c@example.com',
                                amount=100, recoverable=True),
                ])
                self.assertFalse(rows[0].recoverable)
                self.assertIn(reason, rows[0].suppression_reasons)
                self.assertEqual(summarize(rows)['actionable_opportunities'], 0)

    def test_source_specific_missing_identity_does_not_override_verified_source(self):
        rows = merge_evidence([
            EvidenceRef('stripe', 'pi', external_key='booking:1',
                        suppression_reason='missing_customer_identity'),
            EvidenceRef('crm', 'quote', external_key='booking:1',
                        customer_id='C1', amount=100, recoverable=True),
        ])
        self.assertTrue(rows[0].recoverable)
