# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"


    l10n_mx_supplier_cfdi_uuid = fields.Char(string='Fiscal Folio Proveedor', copy=False, readonly=True,)


    def action_create_invoice_from_po(self):
        """Create the invoice associated to the PO.
        """
        factura = self.env['account.move'].create({
            'partner_id': self.partner_id.id,
            'purchase_id': self.id,
            'account_id': self.partner_id.property_account_payable_id.id,
            'type': 'in_invoice',
        })
        factura.purchase_order_change()
        _logger.info(factura)
        _logger.info('factura data.-.-.-.-.-.-')
        return factura