# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = "account.move"


    l10n_mx_supplier_cfdi_uuid = fields.Char(string='Fiscal Folio Proveedor', copy=False, readonly=True,)