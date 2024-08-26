# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_recurring_invoice(self, automatic=False, batch_size=30):
        if self:
            all_subscriptions = self.filtered(
                lambda so: so.is_subscription and
                           so.subscription_management != 'upsell' and
                           not so.payment_exception)
        else:
            search_domain = self._recurring_invoice_domain()
            all_subscriptions = self.search(search_domain, limit=batch_size + 1)
            need_cron_trigger = len(all_subscriptions) > batch_size
            if need_cron_trigger:
                all_subscriptions = all_subscriptions[:batch_size]
        draft_invoices = all_subscriptions.invoice_ids.filtered(
            lambda am: am.state == 'draft')
        draft_invoices.write({'state': 'cancel'})
        invoices = super()._create_recurring_invoice(automatic, batch_size)
        draft_invoices.write({'state': 'draft'})
        all_subscriptions._update_next_invoice_date()
        return invoices

    def _handle_automatic_invoices(self, auto_commit, invoices):
        # remove auto_post invoice created by cron job
        existing_invoices = super(SaleOrder, self.filtered(
            lambda x: x.payment_token_id))._handle_automatic_invoices(
            auto_commit, invoices)
        for order in self.filtered(lambda so: not so.payment_token_id):
            order.with_context(mail_notrack=True).write(
                {'payment_exception': True})
        return existing_invoices
