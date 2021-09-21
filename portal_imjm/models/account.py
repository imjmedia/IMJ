# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = "account.move"


    l10n_mx_supplier_cfdi_uuid = fields.Char(string='Fiscal Folio Proveedor', copy=False, readonly=True,)


    def action_create_invoice_from_po(self, order_rec):
        """Create the invoice associated to the PO.
        """
        factura = self.env['account.move'].create({
            'partner_id': order_rec.partner_id.id,
            'purchase_id': order_rec.id,
            'type': 'in_invoice',
            'date': fields.Date.today(),
            'invoice_origin': order_rec.name,
        })
        po_lines = order_rec.order_line - factura.line_ids.mapped('purchase_line_id')
        new_lines = self.env['account.move.line']
        for line in po_lines.filtered(lambda l: not l.display_type):
            new_line = new_lines.new(line._prepare_account_move_line(self))
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()
        return factura