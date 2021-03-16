# -*- coding: utf-8 -*-

from odoo import fields, models, api, SUPERUSER_ID, _


class AccountMove(models.Model):
    _inherit = 'account.move'


    def l10n_mx_edi_is_required(self):
        result = super(AccountMove, self).l10n_mx_edi_is_required()
        return result and not self.journal_id.not_invoice_sign