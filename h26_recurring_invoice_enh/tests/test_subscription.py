# -*- coding: utf-8 -*-

import datetime
from freezegun import freeze_time

from odoo.addons.sale_subscription.tests.common_sale_subscription import TestSubscriptionCommon
from odoo.tests import tagged


@tagged('-at_install', 'post_install')
class TestSubscription(TestSubscriptionCommon):
    def test_create_multi_draft_invoice_manual(self):
        """
            Manually create multiple draft invoices for subscription
            with monthly recurrence.
        """
        with freeze_time("2024-08-26"):
            self.subscription.write({'recurrence_id': self.recurrence_month.id,
                                     'start_date': '2024-08-26',
                                     'next_invoice_date': '2024-08-26'})
            self.subscription.action_confirm()
            first_draft_inv = self.subscription._create_recurring_invoice()

            self.assertTrue(first_draft_inv)
            self.assertEqual(first_draft_inv.state, 'draft')
            self.assertEqual(self.subscription.next_invoice_date,
                             datetime.date(2024, 9, 26))

        with freeze_time("2024-09-26"):
            second_draft_inv = self.subscription._create_recurring_invoice()
            self.assertTrue(second_draft_inv)
            self.assertEqual(second_draft_inv.state, 'draft')
            self.assertEqual(self.subscription.next_invoice_date,
                             datetime.date(2024, 10, 26))

        with freeze_time("2024-10-26"):
            third_draft_inv = self.subscription._create_recurring_invoice()
            self.assertTrue(third_draft_inv)
            self.assertEqual(third_draft_inv.state, 'draft')
            self.assertEqual(self.subscription.next_invoice_date,
                             datetime.date(2024, 11, 26))
        all_inv = self.subscription.invoice_ids.sorted('date')
        data_inv = [(inv.state,
                     inv.invoice_line_ids.mapped('subscription_start_date'),
                     inv.invoice_line_ids.mapped('subscription_end_date')
                     ) for inv in all_inv]
        self.assertEqual(data_inv, [
            ('draft', [datetime.date(2024, 8, 26), datetime.date(2024, 8, 26)],
             [datetime.date(2024, 9, 25), datetime.date(2024, 9, 25)]),
            ('draft', [datetime.date(2024, 9, 26), datetime.date(2024, 9, 26)],
             [datetime.date(2024, 10, 25), datetime.date(2024, 10, 25)]),
            ('draft', [datetime.date(2024, 10, 26), datetime.date(2024, 10, 26)],
            [datetime.date(2024, 11, 25), datetime.date(2024, 11, 25)]),
        ])

    def test_create_multi_draft_invoice_cron_job(self):
        """
            Create multiple draft invoices for subscriptions with weekly
            recurrence by scheduled action.
        """
        with freeze_time("2024-08-26"):
            self.subscription.write({'recurrence_id': self.recurrence_week.id,
                                     'start_date': '2024-08-26',
                                     'next_invoice_date': '2024-08-26'})
            self.subscription.action_confirm()
            self.env['sale.order']._cron_recurring_create_invoice()
            inv = self.subscription.invoice_ids
            self.assertTrue(inv)
            self.assertTrue(len(inv), 1)
            self.assertEqual(inv.state, 'draft')
            self.assertEqual(self.subscription.next_invoice_date,
                             datetime.date(2024, 9, 2))

        with freeze_time("2024-08-27"):
            self.env['sale.order']._cron_recurring_create_invoice()
            inv = self.subscription.invoice_ids
            self.assertTrue(len(inv), 1)

        with freeze_time("2024-09-02"):
            self.env['sale.order']._cron_recurring_create_invoice()
            inv = self.subscription.invoice_ids

            self.assertTrue(inv)
            self.assertTrue(len(inv), 2)
            self.assertEqual(inv[-1].state, 'draft')
            self.assertEqual(self.subscription.next_invoice_date,
                             datetime.date(2024, 9, 9))

        with freeze_time("2024-09-09"):
            self.env['sale.order']._cron_recurring_create_invoice()
            inv = self.subscription.invoice_ids

            self.assertTrue(inv)
            self.assertTrue(len(inv), 3)
            self.assertEqual(inv[-1].state, 'draft')
            self.assertEqual(self.subscription.next_invoice_date,
                             datetime.date(2024, 9, 16))
        all_inv = self.subscription.invoice_ids.sorted('date')
        data_inv = [(inv.state,
                     inv.invoice_line_ids.mapped('subscription_start_date'),
                     inv.invoice_line_ids.mapped('subscription_end_date')
                     ) for inv in all_inv]
        self.assertEqual(data_inv, [
            ('draft', [datetime.date(2024, 8, 26), datetime.date(2024, 8, 26)],
             [datetime.date(2024, 9, 1), datetime.date(2024, 9, 1)]),
            ('draft', [datetime.date(2024, 9, 2), datetime.date(2024, 9, 2)],
             [datetime.date(2024, 9, 8), datetime.date(2024, 9, 8)]),
            ('draft', [datetime.date(2024, 9, 9), datetime.date(2024, 9, 9)],
             [datetime.date(2024, 9, 15), datetime.date(2024, 9, 15)]),
        ])
