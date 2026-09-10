import unittest
from revenue_recovery.ledger import merge_evidence
from revenue_recovery.ledger_adapters import from_stripe_signal
from revenue_recovery.stripe_source import from_payment_intent
from revenue_recovery.telemetry import jarvis_snapshot


class StripeCanonicalizationTests(unittest.TestCase):
    def _signal(self, source_id: str, booking_id: str):
        return from_payment_intent({
            'id': source_id,
            'amount': 10000,
            'currency': 'usd',
            'status': 'requires_payment_method',
            'livemode': True,
            'customer': None,
            'receipt_email': None,
            'last_payment_error': None,
            'latest_charge': None,
            'metadata': {'booking_id': booking_id},
        })

    def test_two_stripe_payment_intents_for_same_booking_merge_once(self):
        signals = [
            self._signal('pi_preview_1', '584'),
            self._signal('pi_preview_2', '584'),
        ]
        refs = [from_stripe_signal(signal) for signal in signals]
        rows = merge_evidence(refs)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].identity_key, 'external:booking:584')
        self.assertEqual(len(rows[0].source_refs), 2)
        self.assertFalse(rows[0].recoverable)
        self.assertEqual(rows[0].recoverable_value_identified, 0.0)
        self.assertEqual(rows[0].suppression_reasons, ['missing_customer_identity'])

    def test_telemetry_counts_canonical_opportunity_not_source_signals(self):
        signals = [
            self._signal('pi_preview_1', '584'),
            self._signal('pi_preview_2', '584'),
        ]
        rows = merge_evidence(from_stripe_signal(signal) for signal in signals)
        snapshot = jarvis_snapshot(rows, source_commit='test', generated_at='2026-09-10T18:40:00Z')

        self.assertEqual(snapshot['metrics']['canonical_opportunities'], 1)
        self.assertEqual(snapshot['metrics']['ready_recovery_opportunities'], 0)
        self.assertEqual(snapshot['metrics']['suppressed_opportunities'], 1)
        self.assertEqual(snapshot['metrics']['recoverable_value_identified'], 0.0)
        self.assertEqual(snapshot['metrics']['verified_recovered_revenue'], 0.0)
        self.assertEqual(snapshot['suppression_counts'], {'missing_customer_identity': 1})


if __name__ == '__main__':
    unittest.main()
