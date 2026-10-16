from dataclasses import replace
import unittest

from revenue_recovery.stripe_source import from_invoice, from_payment_intent, summarize


class StripeCurrencyTests(unittest.TestCase):
    def invoice(self, **updates):
        return {'id':'in_1','status':'open','amount_remaining':5000,'currency':'usd',
                'customer':'cus_1','customer_email':'c@example.com','livemode':True, **updates}

    def test_usd_minor_units_are_converted(self):
        self.assertEqual(from_invoice(self.invoice(amount_remaining=12345)).amount,123.45)

    def test_unsupported_and_missing_currencies_are_rejected(self):
        for currency in ('jpy','kwd','eur',''):
            with self.subTest(currency=currency):
                with self.assertRaisesRegex(ValueError,'unsupported_currency'):
                    from_invoice(self.invoice(currency=currency))
                with self.assertRaisesRegex(ValueError,'unsupported_currency'):
                    from_payment_intent({'amount':100,'currency':currency})

    def test_invalid_minor_unit_values_are_rejected(self):
        for amount in (float('nan'),float('inf'),float('-inf'),-100,1.5):
            with self.subTest(amount=amount):
                with self.assertRaisesRegex(ValueError,'invalid_minor_unit_amount'):
                    from_invoice(self.invoice(amount_remaining=amount))

    def test_raw_signal_summary_never_adds_different_currencies(self):
        usd=from_invoice(self.invoice())
        eur=replace(usd,source_id='in_eur',amount=75,currency='EUR')
        report=summarize([usd,eur])
        self.assertIsNone(report['recoverable_value_identified'])
        self.assertEqual(report['currency'],'MIXED')
        self.assertEqual(report['amounts_by_currency'],{'USD':50,'EUR':75})
